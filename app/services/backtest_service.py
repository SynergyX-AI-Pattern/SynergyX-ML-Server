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
        if request.startDate > request.endDate:
            logger.warning(f"[Service] 기간 오류: startDate {request.startDate} > endDate {request.endDate}")
            raise APIException(ErrorStatus.INVALID_DATE_RANGE)

        stock_obj = get_stock_by_id(db, stock_id)
        if not stock_obj:
            logger.warning(f"[Service] 존재하지 않는 종목 ID: {stock_id}")
            raise APIException(ErrorStatus.STOCK_NOT_FOUND)

        pattern_obj = get_pattern_by_id(db, pattern_id)
        if not pattern_obj:
            logger.warning(f"[Service] 존재하지 않는 패턴 ID: {pattern_id}")

        unit = pattern_obj.period_unit.name
        value = pattern_obj.period_value
        BacktestService._validate_unit(unit, value)

        raw_timestamps, raw_closes = BacktestService._fetch_timeseries(db, stock_id, request.startDate, request.endDate)
        timestamps, closes = BacktestService._resample_series(raw_timestamps, raw_closes, unit, value)

        idxes, distances = BacktestService._find_match_indices(pattern_obj.points, closes, pattern_obj.tolerance)

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

        Returns:
            타임스탬프 리스트, 종가 리스트
        """
        rows = get_stock_timeseries(db, stock_id, start_date, end_date)
        if not rows:
            raise APIException(ErrorStatus.STOCK_OHLCV_NOT_FOUND)
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
        15분봉 데이터를 사용자 설정 단위로 리샘플링합니다.
        - MINUTE: 그대로 반환
        - HOUR / DAY: 주기 단위마다 마지막 종가 기준으로 집계

        Returns:
            리샘플링된 시계열 데이터
        """
        df = pd.DataFrame({'timestamp': timestamps, 'close': closes})
        df.set_index('timestamp', inplace=True)
        if unit == 'MINUTE':
            return timestamps, closes
        rule = f"{value}{ 'h' if unit=='HOUR' else 'D' }"
        agg = df['close'].resample(rule).last().dropna()
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
            closes: 비교 대상 시계열
            tolerance: 허용 가능한 DTW 거리 한계

        Returns:
            시작 인덱스 리스트, 해당 거리 리스트
        """
        pattern_length = len(pattern)
        norm_pat = BacktestService._zscore_normalize(pattern)
        if norm_pat is None:
            return [], []
        idxes, distances = [], []
        last_end = -1
        for i in range(len(closes) - pattern_length  + 1):
            if i <= last_end:
                continue
            win = closes[i:i+pattern_length ]
            norm_win = BacktestService._zscore_normalize(win)
            if norm_win is None:
                continue
            dist_value, _ = fastdtw(norm_pat, norm_win, dist=lambda a, b: abs(a - b))
            if dist_value <= tolerance:
                idxes.append(i)
                distances.append(distances)
                last_end = i + pattern_length  - 1
        return idxes, distances

    @staticmethod
    def _zscore_normalize(sequence: List[float]) -> Optional[List[float]]:
        """
        z-score 정규화를 수행합니다.

        Returns:
            정규화된 시계열
            if 분산이 0에 가까우면 None
        """
        mean = sum(sequence) / len(sequence)
        var = sum((x - mean) ** 2 for x in sequence) / len(sequence)
        if var < 1e-8:
            return None
        std = var ** 0.5
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
        for idx in idxes:
            entry_i = idx + pat_len - 1
            if entry_i >= len(closes):
                continue
            entry_time = timestamps[entry_i]
            if unit == 'DAY':
                tgt = entry_time + timedelta(days=value)
            elif unit == 'HOUR':
                tgt = entry_time + timedelta(hours=value)
            else:
                tgt = entry_time + timedelta(minutes=value)
            pos = bisect_left(timestamps, tgt)
            if pos >= len(closes): pos = len(closes) - 1
            elif pos > 0 and (timestamps[pos] - tgt) > (tgt - timestamps[pos-1]): pos -= 1
            entry_p, exit_p = closes[entry_i], closes[pos]
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
