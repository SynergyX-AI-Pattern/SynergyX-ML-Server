import logging
from app.schemas.emotion_diary import EmotionDiaryResponse
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus
from app.services.external.gpt_service import GPTService

logger = logging.getLogger(__name__)

class EmotionDiaryService:
    """
    감정 일기 분석을 수행합니다.
    """

    @staticmethod
    def analyze_emotion(content: str) -> EmotionDiaryResponse:
        """
        ChatGPT API를 이용해 감정 분석 결과를 반환합니다.

        Parameters:
            content: 일기 내용

        Returns:
            EmotionDiaryResponse: 감정, 요약, 피드백

        Raises:
            APIException: GPT 응답 실패 시
        """
        try:
            result = GPTService.analyze_emotion_diary(content)
            return EmotionDiaryResponse(
                emotion=result["emotion"],
                summary=result["summary"],
                feedback=result["feedback"]
            )
        except APIException as e:
            raise e
        except Exception as e:
            logger.error(f"[EmotionDiaryService] 감정 분석 실패: {e}")
            raise APIException(ErrorStatus.GPT_API_ERROR) from e
