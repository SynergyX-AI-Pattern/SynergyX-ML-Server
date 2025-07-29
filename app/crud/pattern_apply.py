from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from app.models.pattern_apply import PatternApply

def get_applies(db: Session):
    """
    종목-패턴이 매핑된 패턴 중
    알림 설정이 켜져있고,
    감지 시작일이 현재 시간 이전인 패턴 조회
    """

    kst_now = datetime.now(timezone(timedelta(hours=9)))

    return (
        db.query(PatternApply)
        .filter(
            PatternApply.is_alert_enabled,
            PatternApply.entry_at <= kst_now
        )
        .all()
    )
