from fastapi import APIRouter, UploadFile, File, Depends
from app.api_payload.code.error_status import ErrorStatus
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.api_payload.code.success_status import SuccessStatus
from app.core.response import success_response
from app.exceptions.base import APIException
from app.schemas.base_response import BaseResponse
from app.schemas.image_search import ImageSearchResponse
from app.services.image_search_service import ImageSearchService

router = APIRouter()

@router.post(
    "/search-by-image",
    response_model=BaseResponse,
    summary="이미지 기반 종목 검색",
    description="""
                업로드된 이미지로부터 브랜드를 인식하여 종목 정보를 반환합니다.
                최대 20MB 파일만 업로드 가능합니다.
    """,
    tags=["Stock"]
)
async def search_stock_by_image(
        image: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    contents = await image.read()
    MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB

    # 파일 크기 제한(20MB)

    if len(contents) > MAX_IMAGE_SIZE:
        raise APIException(ErrorStatus.FILE_TOO_LARGE)

    result: ImageSearchResponse = ImageSearchService.search_stock_by_image(contents, db)

    return success_response(
        data=result,
        status=SuccessStatus.IMAGE_SEARCH_SUCCESS
    )