from sqlalchemy import Column, BigInteger, Float, JSON, ForeignKey
from app.models.base_model import BaseTimeModel
from sqlalchemy.orm import relationship, Mapped

class StockDetail(BaseTimeModel):
    __tablename__ = "stock_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_id = Column(BigInteger, ForeignKey("stock.id"), nullable=False, unique=True)

    price = Column(Float, nullable=True)
    change_rate = Column(Float, nullable=True)
    financial_data = Column(JSON, nullable=True)
    change_amount = Column(Float, nullable=True)
    version = Column(BigInteger, nullable=True)

    ai_avg_increase = Column(Float, nullable=True, default=None)
    ai_rank = Column(BigInteger, nullable=True, default=None)

    # 관계
    stock = relationship("Stock", back_populates="stock_detail")
