from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, UniqueConstraint, DateTime, Float
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTimeModel

class PatternApply(BaseTimeModel):
    __tablename__ = "pattern_apply"
    __table_args__ = (
        UniqueConstraint("stock_id", "pattern_id", name="uq_stock_pattern"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    pattern_id = Column(BigInteger, ForeignKey("pattern.id"), nullable=False)

    stock_id = Column(BigInteger, ForeignKey("stock.id"), nullable=False)

    is_alert_enabled = Column(Boolean, nullable=False, default=False)
    entry_at = Column(DateTime, nullable=False)
    entry_price = Column(Float, nullable=False)
    min_valid_return = Column(Float, nullable=False)

    pattern = relationship("Pattern", back_populates="pattern_applies")
    stock = relationship("Stock", back_populates="pattern_applies")
    detection_results = relationship("PatternDetectionLog", back_populates="pattern_apply")