from sqlalchemy import Column, BigInteger, Float, Boolean, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.models.base_model import BaseTimeModel
from app.models.pattern import PeriodUnit

class PatternDetectionLog(BaseTimeModel):
    __tablename__ = "pattern_detection_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    pattern_apply_id = Column(BigInteger, ForeignKey("pattern_apply.id", ondelete="CASCADE"), nullable=False)

    detected_at = Column(DateTime, nullable=False)

    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    return_rate = Column(Float, nullable=False)

    unit = Column(SqlEnum(PeriodUnit, name="period_unit"), nullable=False)
    value = Column(BigInteger, nullable=False)

    is_notification_sent = Column(Boolean, nullable=False, default=False)
    notification_sent_at = Column(DateTime, nullable=True)

    # 관계 설정
    pattern_apply = relationship("PatternApply", back_populates="detection_results")