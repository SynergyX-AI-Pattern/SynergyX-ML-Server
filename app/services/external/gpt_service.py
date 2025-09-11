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
            "아래 키워드를 보고 가장 관련 있는 기업이나 브랜드를 추론해줘.\n"
            "응답 규칙은 반드시 다음과 같이 해.\n\n" 
            "1. 한국 증시에 상장된 KOSPI 100 종목일 경우, 종목명만 정확하게 대답 (예: 삼성전자, LG화학).\n"
            "2. 한국 증시에 상장 되었지만 KOSPI 100에 없는 경우, 종목명만 정확하게 대답(예: 카카오게임즈)"
            "3. 해외 증시에 상장된 회사인 경우, 정식 영문명과 티커(symbol)를 함께 대답 (예: Apple Inc. (AAPL), Starbucks Corporation (SBUX)).\n"
            "4. 상장사가 아닌 브랜드/기업일 경우, '비상장:{브랜드명}' 형식으로 대답 (예: 비상장:에픽게임즈, 비상장:뉴발란스).\n"
            "5. 판단할 수 없을 경우, '모름' 이라고 대답\n\n"
            f"키워드 목록: {', '.join(keywords)}\n\n"
            "반드시 위 규칙대로만 한 줄로 대답하고, 그 외 설명은 하지 마."
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

