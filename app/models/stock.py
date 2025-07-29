from sqlalchemy import Column, String, BigInteger
from app.models.base_model import BaseTimeModel
from sqlalchemy.orm import relationship


class Stock(BaseTimeModel):
    __tablename__ = "stock"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)

    # 관계 설정
    predictions = relationship("Prediction", back_populates="stock")
    pattern_applies = relationship("PatternApply", back_populates="stock")
