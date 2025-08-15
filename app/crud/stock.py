from difflib import get_close_matches
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.stock import Stock


def get_stock_by_id(db: Session, stock_id: int) -> Stock | None:
    """
    stock_id 기준으로 종목 정보를 조회합니다.
    """
    return db.query(Stock).filter(Stock.id == stock_id).first()

def get_stock_by_name(db: Session, name: str) -> Stock | None:
    """
    종목명 기준으로 종목 정보를 조회합니다.
    """

    # 입력 정규화
    # 공백 제거 및 대소문자 무시
    normalized_name = name.replace(" ", "").lower()

    # 1차 : 정확히 일치할 경우 반환
    stock = (
        db.query(Stock)
        .filter(func.replace(func.lower(Stock.name), " ", "") == normalized_name)
        .first()
    )
    if stock:
        return stock

    # 2차 : 유사도 기반 매칭 결과 반환
    all_stock_names = db.query(Stock.name).all()
    name_list = [str(row[0]) for row in all_stock_names]
    close_matches = get_close_matches(name, name_list, n=1, cutoff=0.6) # 유사도 60% 이상

    if close_matches:
        return db.query(Stock).filter(Stock.name == close_matches[0]).first()

    # 없을 경우 None 리턴
    return None

