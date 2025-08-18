import logging
from openai import OpenAI

from app.api_payload.code.error_status import ErrorStatus
from app.core.config import settings
import json

from app.exceptions.base import APIException

logger = logging.getLogger(__name__)


# GPT 클라이언트 생성
client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


class GPTService:
    @staticmethod
    def infer_brand_name_from_keywords(keywords: list[str]) -> str:
        """
        키워드로 기업명을 추론합니다.
        """
        if not keywords:
            return "모름"

        prompt = (
            "아래 키워드를 보고 어떤 KOSPI 100 상장 종목과 가장 관련이 있는지 추론해줘.\n"
            "반드시 한국 증시에 상장된 **KOSPI 100 종목명 중 하나**로만 대답해야 해.\n"
            "예를 들어, '삼성전자', '삼성바이오로직스', 'LG화학'처럼 종목명만 정확하게 대답해줘.\n\n"
            f"키워드 목록: {', '.join(keywords)}\n\n"
            "설명 없이 종목명만 한 줄로 정확하게 대답해. 그 외 다른 말은 하지 마."
            "키워드가 제공되지 않았거나 판단할 정보가 없는 경우 '모름' 이라고 말해줘."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"[GPTService] GPT API 호출 실패: {e}")
            raise APIException(ErrorStatus.GPT_API_ERROR) from e

    @staticmethod
    def analyze_emotion_diary(content: str) -> dict:
        prompt = f"""
           아래는 사용자가 작성한 투자 관련 일기입니다. 이 내용을 기반으로 다음 정보를 추출해주세요:
           - emotion: 감정을 한국어 단어 리스트로 (예: ["우울", "불안"])
           - summary: 핵심 요약 (한 문장)
           - feedback: 투자 관련 조언 (감정 위로 및 투자 전략 제안)

           반드시 아래 포맷의 JSON 형식으로 응답해:
           {{
             "emotion": [...],
             "summary": "...",
             "feedback": "..."
           }}

           일기 내용:
           \"{content}\"
           """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            message = response.choices[0].message.content.strip()

            # 코드블럭 제거
            if message.startswith("```json"):
                message = message[7:]
            if message.startswith("```"):
                message = message[3:]
            if message.endswith("```"):
                message = message[:-3]
            return json.loads(message)

        except json.JSONDecodeError as e:
            logger.error(f"[GPTService] JSON 파싱 실패: {e}")
            raise APIException(ErrorStatus.GPT_RESPONSE_PARSE_ERROR)

        except Exception as e:
            logger.error(f"[GPTService] GPT API 호출 실패: {e}")
            raise APIException(ErrorStatus.GPT_API_ERROR)

