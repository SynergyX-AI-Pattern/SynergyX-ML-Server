from sqlalchemy.orm import Session
from app.models.pattern import Pattern


def get_pattern_by_id(db: Session, pattern_id: int) -> Pattern | None:
    """
    pattern_id 기준으로 패턴 정보를 조회합니다.
    """
    return db.query(Pattern).filter(Pattern.id == pattern_id).first()
