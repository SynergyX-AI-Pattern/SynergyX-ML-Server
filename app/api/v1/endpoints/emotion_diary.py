from fastapi import APIRouter
from app.schemas.base_response import BaseResponse
from app.core.response import success_response
from app.api_payload.code.success_status import SuccessStatus
from app.schemas.emotion_diary import EmotionDiaryRequest, EmotionDiaryResponse
from app.services.emotion_diary_service import EmotionDiaryService

router = APIRouter()

@router.post(
    "",
    response_model=BaseResponse,
    summary="감정 분석 실행",
    description="투자 일기 내용을 분석하여 감정, 요약, 피드백을 추출합니다.",
    tags=["Emotion Diary"]
)
def analyze_emotion_diary(
    request: EmotionDiaryRequest
):
    result: EmotionDiaryResponse = EmotionDiaryService.analyze_emotion(request.content)
    return success_response(
        data=result,
        status=SuccessStatus.DIARY_ANALYSIS_SUCCESS
    )
