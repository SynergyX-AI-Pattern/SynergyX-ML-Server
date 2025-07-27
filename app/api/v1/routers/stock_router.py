from fastapi import APIRouter
from app.api.v1.endpoints import stock

router = APIRouter()
router.include_router(stock.router, prefix="/stocks", tags=["Stock"])
