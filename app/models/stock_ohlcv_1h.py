from sqlalchemy import Column, BigInteger, DateTime, Float, ForeignKey, UniqueConstraint
from app.models.base_model import BaseTimeModel

class StockOhlcv1h(BaseTimeModel):
    __tablename__ = "stock_ohlcv_1h"

    __table_args__ = (
        UniqueConstraint("stock_id", "timestamp", name="uq_stock_ohlcv_1h_stock_timestamp"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    stock_id = Column(BigInteger, ForeignKey("stock.id"), nullable=False)

    timestamp = Column(DateTime, nullable=False)

    open = Column(Float, nullable=False)

    high = Column(Float, nullable=False)

    low = Column(Float, nullable=False)

    close = Column(Float, nullable=False)

    volume = Column(BigInteger, nullable=False)