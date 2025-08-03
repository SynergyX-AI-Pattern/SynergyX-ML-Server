from sqlalchemy import Column, BigInteger, String, Integer, Float, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTimeModel
import enum


class PeriodUnit(enum.Enum):
    HOUR = "HOUR"
    DAY = "DAY"

class Pattern(BaseTimeModel):
    __tablename__ = "pattern"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    pattern_name = Column(String(255), nullable=False)

    points = Column(JSON, nullable=False)

    tolerance = Column(Float, nullable=False)

    period_value = Column(Integer, nullable=False)

    period_unit = Column(SqlEnum(PeriodUnit), nullable=False)

    # 관계 설정
    pattern_applies = relationship("PatternApply", back_populates="pattern")
