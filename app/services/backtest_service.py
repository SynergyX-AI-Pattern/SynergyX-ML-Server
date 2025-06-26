import logging
from bisect import bisect_left
from datetime import timedelta, datetime, date
from typing import List, Tuple, Optional
import pandas as pd
from fastdtw import fastdtw
from sqlalchemy.orm import Session

from app.crud.stock import get_stock_by_id
from app.crud.pattern import get_pattern_by_id
from app.crud.stock_timeseries import get_stock_timeseries
from app.schemas.backtest import BacktestResponse, BacktestRequest
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus

logger = logging.getLogger(__name__)

class BacktestService:
    """
    백테스트 관련 비즈니스 로직을 처리합니다.
    """
    @staticmethod
    def execute_backtest(stock_id: int, pattern_id: int, request: BacktestRequest, db: Session) -> BacktestResponse:

        # 날짜 유효성 검사
        if request.startDate > request.endDate:
            logger.warning(f"[Service] 기간 오류: startDate {request.startDate} > endDate {request.endDate}")
            raise APIException(ErrorStatus.INVALID_DATE_RANGE)

        # 종목 유효성 검사
        stock_obj = get_stock_by_id(db, stock_id)
        if not stock_obj:
            logger.warning(f"[Service] 존재하지 않는 종목 ID: {stock_id}")
            raise APIException(ErrorStatus.STOCK_NOT_FOUND)

        # 패턴 유효성 검사
        pattern_obj = get_pattern_by_id(db, pattern_id)
        if not pattern_obj:
            logger.warning(f"[Service] 존재하지 않는 패턴 ID: {pattern_id}")
            raise APIException(ErrorStatus.PATTERN_NOT_FOUND)

        # 패턴 단위 및 값 검사
        unit = pattern_obj.period_unit.name
        value = pattern_obj.period_value
        BacktestService._validate_unit(unit, value)

        # 종목 데이터 조회 및 리샘플링
        raw_timestamps, raw_closes = BacktestService._fetch_timeseries(db, stock_id, request.startDate, request.endDate)
        timestamps, closes = BacktestService._resample_series(raw_timestamps, raw_closes, unit, value)

        # dtw 로직
        idxes, distances = BacktestService._find_match_indices(pattern_obj.points, closes, pattern_obj.tolerance)

        # 수익률 계산
        returns = BacktestService._calculate_returns(idxes, closes, timestamps, unit, value, len(pattern_obj.points))

        return BacktestService._aggregate_results(returns, request.startDate, len(idxes))

    @staticmethod
    def _validate_unit(unit: str, value: int):
        """
        사용자 설정 단위(unit)와 값(value)이 유효한지 검증합니다.

        Raises:
            APIException: 유효하지 않은 단위 또는 값일 경우
        """
        if unit == "MINUTE" and value % 15 != 0:
            raise APIException(ErrorStatus.INVALID_UNIT_VALUE)
        if unit in {"HOUR", "DAY"} and value < 1:
            raise APIException(ErrorStatus.INVALID_UNIT_VALUE)
        if unit not in {"MINUTE", "HOUR", "DAY"}:
            raise APIException(ErrorStatus.INVALID_UNIT)

    @staticmethod
    def _fetch_timeseries(
        db: Session,
        stock_id: int,
        start_date: date,
        end_date: date
    ) -> Tuple[List[datetime], List[float]]:
        """
        DB에서 데이터를 조회합니다.

        Parameters:
            db: DB 세션
            stock_id: 조회할 종목 ID
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            타임스탬프 리스트, 종가 리스트

        Raises:
            APIException: 해당 종목의 데이터가 없는 경우
        """
        rows = get_stock_timeseries(db, stock_id, start_date, end_date)
        if not rows:
            raise APIException(ErrorStatus.STOCK_OHLCV_NOT_FOUND)

        # (timestamp, close) 형태로 분리 후 리스트 반환
        timestamps, closes = zip(*rows)
        return list(timestamps), list(closes)

    @staticmethod
    def _resample_series(
        timestamps: List[datetime],
        closes: List[float],
        unit: str,
        value: int
    ) -> Tuple[List[datetime], List[float]]:
        """
        15분봉 데이터를 사용자 설정 단위에 따라 리샘플링합니다.

        Parameters:
            timestamps: 원본 타임스탬프 리스트 (15분 단위 기준)
            closes: 종가 리스트
            unit: 단위
            value: 값

        Returns:
            리샘플링된 타임스탬프 리스트, 종가 리스트
            - MINUTE: 원본 그대로 반환
            - HOUR/DAY: 해당 단위 기준으로 마지막 종가만 추출 (resample().last())
        """
        # 시계열 데이터 프레임 생성, timestamp를 인덱스로 설정
        df = pd.DataFrame({'timestamp': timestamps, 'close': closes})
        df.set_index('timestamp', inplace=True)

        if unit == 'MINUTE':
            return timestamps, closes

        # pandas 리샘플링 규칙 생성
        rule = f"{value}{ 'h' if unit=='HOUR' else 'D' }"

        # 각 구간의 마지막 종가만 추출
        agg = df['close'].resample(rule).last().dropna()

        # 리샘플링 결과 없을 경우 예외 발생
        if agg.empty:
            raise APIException(ErrorStatus.NO_RESAMPLED_DATA)

        # 리스트 변환 후 반환
        return list(agg.index), list(agg.values)

    @staticmethod
    def _find_match_indices(
        pattern: List[float],
        closes: List[float],
        tolerance: float
    ) -> Tuple[List[int], List[float]]:
        """
        DTW를 통해 패턴과 유사한 구간 탐색합니다.

        Parameters:
            pattern: 사용자 패턴
            closes: 비교 대상 종가 데이터
            tolerance: 허용 가능한 DTW 거리 상한값

        Returns:
            시작 인덱스 리스트, 해당 거리 리스트

        Raises:
            APIException:
                - 시계열이 패턴보다 짧은 경우
                - 패턴의 분산이 0에 가까워 정규화가 불가능할 경우
        """
        pattern_length = len(pattern)

        # 비교 대상 데이터가 패턴보다 짧은 경우
        if len(closes) < pattern_length:
            raise APIException(ErrorStatus.NOT_ENOUGH_DATA)

        # 패턴을 z-score 정규화 (평균 0, 표준편차 1)
        norm_pat = BacktestService._zscore_normalize(pattern)

        # 패턴 값이 모두 동일한 경우
        if norm_pat is None:
            raise APIException(ErrorStatus.PATTERN_TOO_FLAT)

        idxes, distances = [], []
        last_end = -1

        # 슬라이딩 윈도우 방식으로 유사 구간 탐색
        for i in range(len(closes) - pattern_length  + 1):
            if i <= last_end:
                # 이전 매칭 구간과 겹치지 않도록 넘김
                continue

            win = closes[i:i+pattern_length ]
            norm_win = BacktestService._zscore_normalize(win)

            # 분산 0일 경우
            if norm_win is None:
                continue

            # DTW 로직 구현
            dist_value, _ = fastdtw(norm_pat, norm_win, dist=lambda a, b: abs(a - b))
            if dist_value <= tolerance:
                idxes.append(i)
                distances.append(dist_value)
                last_end = i + pattern_length  - 1 # 매칭 구간 이후 다시 탐색
        return idxes, distances

    @staticmethod
    def _zscore_normalize(sequence: List[float]) -> Optional[List[float]]:
        """
        z-score 정규화를 수행합니다.

        Returns:
            - 정규화된 시계열 데이터
            if 분산이 거의 0이면 (모든 값이 거의 동일하면) None 반환
        """
        mean = sum(sequence) / len(sequence) # 평균 계산
        var = sum((x - mean) ** 2 for x in sequence) / len(sequence) # 분산 계산

        # 분산 0일 경우
        if var < 1e-8:
            return None
        std = var ** 0.5 # 표준 편차 계산
        return [(x - mean) / std for x in sequence]

    @staticmethod
    def _calculate_returns(
        idxes: List[int],
        closes: List[float],
        timestamps: List[datetime],
        unit: str,
        value: int,
        pat_len: int
    ) -> List[Tuple[datetime, float]]:
        """
        각 매칭 구간의 수익률 계산합니다.

        Parameters:
            idxes: 매칭 시작 인덱스 리스트
            closes: 종가
            timestamps: 타임스탬프
            unit, value: 단위, 값
            pat_len: 패턴 길이

        Returns:
            (진입 시점, 수익률) 리스트
        """
        returns = []

        # 매칭 구간 반복
        for idx in idxes:
            # 진입 시점 : 패턴의 마지막 지점
            entry_i = idx + pat_len - 1
            # 진입 시점이 데이터 범위 벗어나는 경우 넘김
            if entry_i >= len(closes):
                continue
            # 진입 시간 설정 (매수 시간)
            entry_time = timestamps[entry_i]

            # 단위에 따른 목표 계산 (매도 목표 시간)
            if unit == 'DAY':
                tgt = entry_time + timedelta(days=value)
            elif unit == 'HOUR':
                tgt = entry_time + timedelta(hours=value)
            else:
                tgt = entry_time + timedelta(minutes=value)

            # 적절한 청산(매도) 시점 찾기 (이진 탐색)
            pos = bisect_left(timestamps, tgt)

            # 범위 초과 시 마지막 종가로 설정
            if pos >= len(closes): pos = len(closes) - 1
            # 이전 시점이 더 가까우면 뒤로 이동
            elif pos > 0 and (timestamps[pos] - tgt) > (tgt - timestamps[pos-1]): pos -= 1
            # 진입가, 청산가 활용하여 수익률 계산
            entry_p, exit_p = closes[entry_i], closes[pos]
            # 수익률
            returns.append((entry_time, (exit_p-entry_p)/entry_p * 100))
        return returns

    @staticmethod
    def _aggregate_results(
        returns: List[Tuple[datetime, float]],
        start_date: date,
        match_count: int
    ) -> BacktestResponse:
        """
        최종 응답을 반환합니다.

        Parameters:
            returns: (진입 시점, 수익률) 리스트
            match_count: 매칭된 구간 수

        Returns:
            BacktestResponse
        """
        if not returns:
            return BacktestResponse(
                matchedCount=match_count,
                winRate=0.0,
                averageReturn=0.0,
                maxReturn=0.0,
                maxReturnDate=start_date,
                minReturn=0.0,
                minReturnDate=start_date,
                totalReturn=0.0,
                lastMatchedDate=start_date,
                lastMatchedReturn=0.0
            )
        dates, vals = zip(*returns)
        wins = [v for v in vals if v > 0]
        return BacktestResponse(
            matchedCount=match_count,
            winRate=len(wins)/len(vals) * 100,
            averageReturn=sum(vals)/len(vals),
            maxReturn=max(vals),
            maxReturnDate=dates[vals.index(max(vals))].date(),
            minReturn=min(vals),
            minReturnDate=dates[vals.index(min(vals))].date(),
            totalReturn=sum(vals),
            lastMatchedDate=dates[-1].date(),
            lastMatchedReturn=vals[-1]
        )
