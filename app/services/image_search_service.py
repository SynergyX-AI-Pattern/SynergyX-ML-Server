import logging, re
from sqlalchemy.orm import Session
from app.crud.stock import get_stock_by_name
from app.schemas.image_search import ImageSearchResponse, StockStatus
from app.services.external.gpt_service import GPTService
from app.services.external.vision_service import VisionService

logger = logging.getLogger(__name__)


class ImageSearchService:
    @staticmethod
    def search_stock_by_image(contents: bytes, db: Session) -> ImageSearchResponse:
        """
        이미지 → Vision api → GPT api → 종목 검색
        """
        # 키워드 추출
        keywords_dict = VisionService.extract_keywords(contents)

        # 키워드 정규화
        keyword_list = VisionService.normalize_keywords(keywords_dict)

        # 종목 추론
        brand_name = GPTService.infer_brand_name_from_keywords(keyword_list)

        # 비상장 prefix 처리
        clean_name = re.sub(r'^\s*\[?비상장\]?\s*:?\s*', '', brand_name).strip()
        if clean_name != brand_name:
            logger.info(f"[ImageSearchService] 비상장 기업 : {clean_name}")
            return ImageSearchResponse(
                id=None,
                name=clean_name,
                imageUrl=None,
                status=StockStatus.UNLISTED
            )

        elif brand_name == "모름":
            logger.info(f"[ImageSearchService] 이미지 분석 실패")
            return ImageSearchResponse(
                id=None,
                name="모름",
                imageUrl=None,
                status=StockStatus.UNKNOWN
            )

        else:
            # 종목 검색
            logger.debug(f"[ImageSearchService] {brand_name}으로 종목 검색 시작")
            stock = get_stock_by_name(db, brand_name)

            # KOSPI100
            if stock:
                logger.info(f"[ImageSearchService] 매칭된 종목 : {stock.name}")
                return ImageSearchResponse(
                    id=stock.id,
                    name=stock.name,
                    imageUrl=stock.image_url,
                    status=StockStatus.LISTED
                )

            # KOSPI100 미해당 상장자
            else:
                logger.info(f"[ImageSearchService] KOSPI100 미해당 기업 : {brand_name}")
                return ImageSearchResponse(
                    id=None,
                    name=brand_name,
                    imageUrl=None,
                    status=StockStatus.LISTED_OUTSIDE
                )