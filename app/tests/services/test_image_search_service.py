import os
import pytest
from dotenv import load_dotenv
from unittest.mock import patch
from types import SimpleNamespace
from app.db.session import SessionLocal
from app.services.image_search_service import ImageSearchService
from app.exceptions.base import APIException
from app.api_payload.code.error_status import ErrorStatus

# .env 로드
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_search_stock_by_image_success(db):
    """
    [성공] Vision, GPT mock 결과로 매칭되는 종목 존재할 때 정상 조회
    """
    dummy_bytes = b"fake-image-bytes"

    with patch("app.services.image_search_service.VisionService.extract_keywords") as mock_vision, \
         patch("app.services.image_search_service.VisionService.normalize_keywords") as mock_normalize, \
         patch("app.services.image_search_service.GPTService.infer_brand_name_from_keywords") as mock_gpt, \
         patch("app.services.image_search_service.get_stock_by_name") as mock_get_stock_by_name:

        mock_vision.return_value = {"label": ["Galaxy"], "text": [], "logo": [], "web": []}
        mock_normalize.return_value = ["Galaxy"]
        mock_gpt.return_value = "삼성전자"
        mock_get_stock_by_name.return_value = SimpleNamespace(id=1, name="삼성전자")

        result = ImageSearchService.search_stock_by_image(dummy_bytes, db)

        assert getattr(result, "id", None) == 1


def test_search_stock_by_image_not_found(db):
    """
    [실패] Vision, GPT mock 결과로 일치하는 종목이 없을 때 예외 발생
    """
    dummy_bytes = b"fake-image-bytes"

    with patch("app.services.image_search_service.VisionService.extract_keywords") as mock_vision, \
         patch("app.services.image_search_service.VisionService.normalize_keywords") as mock_normalize, \
         patch("app.services.image_search_service.GPTService.infer_brand_name_from_keywords") as mock_gpt, \
         patch("app.services.image_search_service.get_stock_by_name") as mock_get_stock_by_name:

        mock_vision.return_value = {"label": ["UnknownBrand"], "text": [], "logo": [], "web": []}
        mock_normalize.return_value = ["UnknownBrand"]
        mock_gpt.return_value = "없는회사"
        mock_get_stock_by_name.return_value = None

        with pytest.raises(APIException) as exc_info:
            ImageSearchService.search_stock_by_image(dummy_bytes, db)

        assert exc_info.value.status == ErrorStatus.STOCK_NOT_FOUND
