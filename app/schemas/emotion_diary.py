from pydantic import BaseModel

class EmotionDiaryRequest(BaseModel):
    content: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "content": "오늘 주식이 너무 떨어져서 너무 슬펐어... 투자하기 무서워."
            }
        }
    }


class EmotionDiaryResponse(BaseModel):
    emotion: list[str]
    summary: str
    feedback: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "emotion": ["불안", "우울"],
                "summary": "주식 하락으로 인한 불안한 감정",
                "feedback": "단기적인 하락에 흔들리지 말고 투자 전략을 재점검해보세요."
            }
        }
    }
