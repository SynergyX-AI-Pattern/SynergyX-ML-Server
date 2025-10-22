import logging
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.api_payload.code.error_status import ErrorStatus
from app.exceptions.base import APIException
from app.crud.stock_timeseries import get_stock_timeseries_by_unit
from app.crud.pattern_apply import get_applies
from app.models.pattern_detection_log import PatternDetectionLog
from app.utils.timeseries_calculator import (
    validate_unit,
    find_match_indices,
)
from app.utils.notification_sender import send_notification_to_spring

logger = logging.getLogger(__name__)


class PatternDetectionService:
    """
    실시간 패턴 감지 관련 비즈니스 로직을 처리합니다.
    """
    @staticmethod
    def detect(db: Session) -> list[dict]:
        """
        감지를 수행한 후, 감지 성공 결과 리스트를 반환합니다.
        - 감지 성공 시 알림 설정을 비활성화합니다.
        """
        results = []
        now = datetime.now(timezone(timedelta(hours=9)))

        # 감지 대상 패턴 불러오기
        applies = get_applies(db)
        if not applies:
            logger.info("[PatternDetection] 감지 대상 없음")
            return []

        # 감지 성공한 패턴
        success_applies = []

        for apply in applies:
            # 각 패턴-종목에 대해 감지 수행
            try:
                result = PatternDetectionService._process_apply(apply, db, now)
                if result:
                    success_applies.append(apply)
                    results.append(result)
            except Exception as e:
                logger.warning(f"[PatternDetection] {apply.stock.name} 감지 중 오류 발생: {e}")
                continue

        # 감지 성공한 패턴은 알림 설정 해제
        for apply in success_applies:
            apply.is_alert_enabled = False

        db.commit()

        return results

    @staticmethod
    def _process_apply(apply, db: Session, now: datetime) -> Optional[dict]:
        """
        감지 대상 패턴-종목에 대해
        진입 시점(entry_at)부터 현재 시점(now)까지 수익률을 계산한 후,
        조건을 만족하면 결과를 반환하고 알림을 전송합니다.
        """
        stock_id = apply.stock_id
        stock_name = apply.stock.name
        pattern_name = apply.pattern.pattern_name
        pattern = apply.pattern.points
        tolerance = apply.pattern.tolerance
        unit = apply.pattern.period_unit.name.upper()
        value = apply.pattern.period_value
        min_valid_return = apply.min_valid_return

        # 진입 시점 기준 정보
        entry_at = apply.entry_at
        entry_price = apply.entry_price

        # 진입 가격이 0일 경우 예외 처리
        if entry_price == 0:
            raise APIException(ErrorStatus.RETURN_CALCULATION_FAILED)

        # 단위/값 유효성 검사 (value가 0이면 에러)
        validate_unit(unit, value)

        # 가격 데이터 불러오기
        closes, timestamps = PatternDetectionService._load_price_data(
            db=db,
            stock_id=stock_id,
            unit=unit,
            entry_at=apply.entry_at,
            now=now
        )

        # 데이터 유효성 검증
        if not closes or not timestamps or len(closes) < len(pattern) * 2:
            return None

        # DTW 매칭
        try:
            idxes, _ = find_match_indices(pattern, closes, tolerance)
        except APIException as e:
            # 데이터 부족 시 감지 생략
            if e.status == ErrorStatus.NOT_ENOUGH_DATA:
                return None
            return None

        # 방향성 검증
        idxes = [
            i for i in idxes
            if PatternDetectionService._same_direction(pattern, closes, i)
        ]

        # 매칭된 구간 없을 시 감지 생략
        if not idxes:
            return None

        # 감지 시점 종가
        current_price = closes[-1]

        # 수익률 계산
        rate_of_return = round(((current_price - entry_price) / entry_price) * 100, 2)

        # 최소 수익률 조건 미충족 시 감지 생략
        if min_valid_return is not None and rate_of_return < min_valid_return:
            return None

        try:
            send_notification_to_spring(
                title=f"[{stock_name}] 패턴 감지!",
                message=f"{stock_name}에 적용한 {pattern_name} 패턴이 감지되었습니다.",
                notification_type="PATTERN_DETECTED"
            )
            is_sent = True
            sent_at = now
        except Exception as e:
            logger.warning(f"[패턴 감지] 알림 전송 실패: {e}")
            is_sent = False
            sent_at = None

        # 패턴 감지 로그
        log = PatternDetectionLog(
            pattern_apply_id=apply.id,
            detected_at=now,
            entry_price=entry_price,
            current_price=current_price,
            return_rate=rate_of_return,
            unit=unit,
            value=value,
            is_notification_sent=is_sent,
            notification_sent_at=sent_at,
        )
        db.add(log)

        return {
            "patternApplyId": apply.id,
            "stockName": stock_name,
            "patternName": pattern_name,
            "entryAt": entry_at.isoformat(),
            "entryPrice": entry_price,
            "detectedAt": now.isoformat(),
            "currentPrice": current_price,
            "return": rate_of_return,
            "unit": unit,
            "value": value
        }

    @staticmethod
    def _same_direction(
            pattern: list[float],
            closes: list[float],
            idx: int
    ) -> bool:
        """
        패턴과 실제 주가의 방향 (상승, 하락)이 일치하는지 검증합니다.
        """

        # 패턴의 방향 (기울기)
        pat_slope = pattern[-1] - pattern[0]

        # 주가의 방향 (기울기)
        seg_slope = closes[idx + len(pattern) - 1] - closes[idx]

        # 부호가 동일하면 동일 방향
        return (pat_slope * seg_slope) > 0

    @staticmethod
    def _load_price_data(
            db: Session,
            stock_id: int,
            unit: str,
            entry_at: datetime,
            now: datetime
    ) -> Tuple[list[float], list[datetime]]:
        """
        진입 시점(entry_at)부터 현재까지의 가격 데이터를 조회합니다.

        Returns:
            - 종가 리스트 (closes)
            - 타임스탬프 리스트 (timestamps)
        """
        rows = get_stock_timeseries_by_unit(
            db=db,
            stock_id=stock_id,
            start_datetime=entry_at,
            end_datetime=now,
            unit=unit
        )

        if not rows:
            raise APIException(ErrorStatus.STOCK_OHLCV_NOT_FOUND)

        timestamps, closes = zip(*rows)
        return list(closes), list(timestamps)