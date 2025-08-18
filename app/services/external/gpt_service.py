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
        system_prompt = (
            "당신은 투자 일기의 감정 분석과 조언을 제공하는 어시스턴트입니다. "
            "다음 형식의 JSON만 반환하세요: "
            '{"emotion": ["..."], "summary": "...", "feedback": "..."} '
            "설명, 코드블록, 추가 텍스트는 절대 포함하지 마세요."
        )

        user_prompt = (
            "아래 일기를 분석해 다음 정보를 추출하세요.\n"
            "- emotion: 감정을 한국어 단어 리스트로 (예: [\"우울\", \"불안\"])\n"
            "- summary: 핵심 요약 (한 문장)\n"
            "- feedback: 투자 관련 조언 (감정 위로 및 투자 전략 제안)\n\n"
            f"일기 내용:\n{content}"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                max_tokens=500,
            )
            message = response.choices[0].message.content.strip()
            data = json.loads(message)

            # 필수 키 존재 및 타입 점검
            if not isinstance(data, dict) or \
               "emotion" not in data or "summary" not in data or "feedback" not in data:
                raise APIException(ErrorStatus.GPT_RESPONSE_PARSE_ERROR)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"[GPTService] JSON 파싱 실패: {e}")
            raise APIException(ErrorStatus.GPT_RESPONSE_PARSE_ERROR) from e

        except Exception as e:
            logger.error(f"[GPTService] GPT API 호출 실패: {e}")
            raise APIException(ErrorStatus.GPT_API_ERROR)

