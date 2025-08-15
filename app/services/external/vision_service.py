import logging, os, re
from google.cloud import vision
from app.core.config import settings

logger = logging.getLogger(__name__)


# Google Cloud Vision API 클라이언트 (지연 초기화)
client: vision.ImageAnnotatorClient | None = None

class VisionService:
    """
    Google Cloud Vision API 연동 서비스입니다.
    이미지에서 라벨, 텍스트, 로고, 웹 정보를 추출합니다.
    """

    @staticmethod
    def extract_keywords(image_bytes: bytes) -> dict[str, list[str]]:
        """
        이미지에서 키워드를 추출합니다.
        """
        global client
        if client is None:
            os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS)
            client = vision.ImageAnnotatorClient()

        # 이미지 바이트 데이터를 이미지 객체로 변환
        image = vision.Image(content=image_bytes)

        # 딕셔너리 초기화
        result = {"label": [], "text": [], "logo": [], "web": []}

        logger.debug("[VisionService] Vision 분석 시작")

        # 라벨
        try:
            label_res = client.label_detection(image=image)
            result["label"] = [l.description for l in label_res.label_annotations]
        except Exception as e:
            logger.warning(f"[VisionService] 라벨 분석 실패: {e}")

        # 텍스트
        try:
            text_res = client.text_detection(image=image)
            result["text"] = [t.description for t in text_res.text_annotations]
        except Exception as e:
            logger.warning(f"[VisionService] 텍스트 분석 실패: {e}")

        # 로고
        try:
            logo_res = client.logo_detection(image=image)
            result["logo"] = [l.description for l in logo_res.logo_annotations]
        except Exception as e:
            logger.warning(f"[VisionService] 로고 분석 실패: {e}")

        # 웹
        try:
            web_res = client.web_detection(image=image)
            if web_res.web_detection and web_res.web_detection.web_entities:
                result["web"] = [w.description for w in web_res.web_detection.web_entities if w.description]
        except Exception as e:
            logger.warning(f"[VisionService] 웹 분석 실패: {e}")

        # 디버그용 로그 출력
        logger.debug(
            f"[VisionService] Vision 분석 완료: "
            f"label={result['label'][:3]}, text={result['text'][:3]}, "
            f"logo={result['logo'][:3]}, web={result['web'][:3]}"
        )
        return result

    @staticmethod
    def normalize_keywords(keyword_sources: dict[str, list[str]]) -> list[str]:
        """
        키워드를 정규화합니다.
        """
        # 중복 제거 set 사용
        all_keywords = set()

        for source_keywords in keyword_sources.values():
            for keyword in source_keywords:
                # 특수문자 제거 (영문/한글/숫자/공백만 허용)
                cleaned = re.sub(r'[^a-zA-Z가-힣0-9\s]', ' ', keyword)

                # 앞뒤 공백 제거 후 단어 단위로 분할
                parts = cleaned.strip().split()

                # 전체 키워드 집합에 추가
                all_keywords.update(parts)

        return list(all_keywords)

