from sqlalchemy import Column, BigInteger, Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base_model import BaseTimeModel


class Prediction(BaseTimeModel):
    __tablename__ = "prediction"

    __table_args__ = (
        UniqueConstraint("stock_id", "target_date", name="uq_stock_target_date"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    stock_id = Column(BigInteger, ForeignKey("stock.id", ondelete="CASCADE"), nullable=False)

    target_date = Column(Date, nullable=False)

    predicted_close = Column(Float, nullable=False)
    predicted_high = Column(Float, nullable=True)
    predicted_low = Column(Float, nullable=True)
    recommended_sell = Column(Float, nullable=False)
    recommended_buy = Column(Float, nullable=False)

    # 관계 설정
    stock = relationship("Stock", back_populates="predictions")
