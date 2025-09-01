import logging
from bisect import bisect_left
from datetime import datetime, date, timedelta, time
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.crud.stock import get_stock_by_id
from app.crud.pattern import get_pattern_by_id
from app.crud.stock_timeseries import get_stock_timeseries_by_unit
from app.schemas.backtest import BacktestResponse, BacktestRequest, HighlightRange
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus
from app.utils.timeseries_calculator import (
    validate_unit,
    find_match_indices,
)

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
        validate_unit(unit, value)

        # 종목 데이터 조회
        timestamps, closes = BacktestService._fetch_timeseries_by_unit(
            db, stock_id, request.startDate, request.endDate, unit
        )

        # dtw 로직
        idxes, _ = find_match_indices(pattern_obj.points, closes, pattern_obj.tolerance)

        # 수익률 계산
        returns = BacktestService._calculate_returns(idxes, closes, timestamps, unit, value, len(pattern_obj.points))

        return BacktestService._aggregate_results(returns, request.startDate, len(idxes))


    @staticmethod
    def _fetch_timeseries_by_unit(
        db: Session,
        stock_id: int,
        start_date: date,
        end_date: date,
        unit: str
    ) -> Tuple[List[datetime], List[float]]:
        """
        DB에서 데이터를 조회합니다.

        Parameters:
            db: DB 세션
            stock_id: 조회할 종목 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            unit: 단위

        Returns:
            타임스탬프 리스트, 종가 리스트

        Raises:
            APIException: 해당 종목의 데이터가 없는 경우
        """

        # 함수 사용을 위한 datetime 변환
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        rows = get_stock_timeseries_by_unit(
            db=db,
            stock_id=stock_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            unit=unit)

        if not rows:
            raise APIException(ErrorStatus.STOCK_OHLCV_NOT_FOUND)

        # (timestamp, close) 형태로 분리 후 리스트 반환
        timestamps, closes = zip(*rows)
        return list(timestamps), list(closes)

    @staticmethod
    def _calculate_returns(
        idxes: List[int],
        closes: List[float],
        timestamps: List[datetime],
        unit: str,
        value: int,
        pat_len: int
    ) -> List[Tuple[datetime, float, datetime, datetime]]:
        """
        각 매칭 구간의 수익률 계산합니다.

        Parameters:
            idxes: 매칭 시작 인덱스 리스트
            closes: 종가
            timestamps: 타임스탬프
            unit, value: 단위, 값
            pat_len: 패턴 길이

        Returns:
            (진입 시점, 수익률, 구간 시작 지점, 구간 종료 지점) 리스트
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
            if pos >= len(closes):
                pos = len(closes) - 1

            # 이전 시점이 더 가까우면 뒤로 이동
            elif pos > 0 and (timestamps[pos] - tgt) > (tgt - timestamps[pos - 1]):
                pos -= 1

            # 진입가, 청산가 활용하여 수익률 계산
            entry_p, exit_p = closes[entry_i], closes[pos]
            ret = (exit_p - entry_p) / entry_p * 100

            # 매칭 구간 저장
            match_start = timestamps[idx]
            match_end = timestamps[entry_i]

            # 수익률 포함 결과 매칭 구간 저장
            returns.append((entry_time, ret, match_start, match_end))

        return returns

    @staticmethod
    def _aggregate_results(
        returns: List[Tuple[datetime, float, datetime, datetime]],
        start_date: date,
        match_count: int
    ) -> BacktestResponse:
        """
        최종 응답을 반환합니다.

        Parameters:
            returns: (진입 시점, 수익률, 구간 시작 지점, 구간 종료 지점) 리스트
            start_date : 시작 날짜
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
                lastMatchedReturn=0.0,
                highlightRange=None
            )
        dates, vals, match_starts, match_ends = zip(*returns)
        wins = [v for v in vals if v > 0]

        max_idx = vals.index(max(vals))

        return BacktestResponse(
            matchedCount=match_count,
            winRate=len(wins)/len(vals) * 100,
            averageReturn=sum(vals)/len(vals),
            maxReturn=max(vals),
            maxReturnDate=dates[max_idx].date(),
            minReturn=min(vals),
            minReturnDate=dates[vals.index(min(vals))].date(),
            totalReturn=sum(vals),
            lastMatchedDate=dates[-1].date(),
            lastMatchedReturn=vals[-1],
            highlightRange=HighlightRange(
                fromDate=match_starts[max_idx].isoformat(),
                toDate=match_ends[max_idx].isoformat()
            )
        )
