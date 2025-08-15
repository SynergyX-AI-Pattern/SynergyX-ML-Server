import logging
from sqlalchemy.orm import Session
from app.crud.stock import get_stock_by_name
from app.exceptions.base import APIException
from app.api_payload.code.error_status import ErrorStatus
from app.schemas.image_search import ImageSearchResponse
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

        # 종목 검색
        logger.debug(f"[ImageSearchService] {brand_name}으로 종목 검색 시작")
        stock = get_stock_by_name(db, brand_name)
        if not stock:
            logger.warning(f"[ImageSearchService] {brand_name}와 일치하는 종목을 찾을 수 없습니다.")
            raise APIException(ErrorStatus.STOCK_NOT_FOUND)
        logger.info(f"[ImageSearchService] 매칭된 종목 : {stock.name}")

        return ImageSearchResponse(
            id = stock.id
        )