from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class BaseTimeModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
