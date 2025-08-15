from fastapi import APIRouter
from app.api.v1.endpoints.stocks import stock, image_search

router = APIRouter()
router.include_router(stock.router, prefix="/stocks", tags=["Stock"])
router.include_router(image_search.router, prefix="/stocks", tags=["Stock"])
