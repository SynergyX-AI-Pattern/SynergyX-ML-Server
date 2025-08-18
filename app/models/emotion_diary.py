from sqlalchemy import Column, BigInteger, Text
from sqlalchemy.dialects.postgresql import JSON

from app.models.base_model import BaseTimeModel

class Pattern(BaseTimeModel):
    __tablename__ = "emotion_diary"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    content = Column(Text, nullable=False)

    emotion = Column(JSON, nullable=False)

    summary = Column(Text, nullable=False)

    feedback = Column(Text, nullable=False)