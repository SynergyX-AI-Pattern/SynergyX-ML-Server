import logging
from openai import OpenAI

from app.api_payload.code.error_status import ErrorStatus
from app.core.config import settings

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
            raise APIException(ErrorStatus.GPT_API_ERROR)

