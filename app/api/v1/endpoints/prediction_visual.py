from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.prediction_visual_service import plot_prediction_graph
from app.services.prediction_visual_service import plot_error_distribution
import pandas as pd

router = APIRouter()


@router.get("/visualize")
def visualize_prediction(response: Response, db: Session = Depends(get_db)):
    query = """
            SELECT p.target_date, p.predicted_close, o.close
            FROM prediction p
                     JOIN stock_ohlcv_1d o
                          ON p.stock_id = o.stock_id
                              AND DATE (o.timestamp) = p.target_date
            WHERE o.timestamp BETWEEN '2025-08-06'
              AND '2025-10-28'
              AND p.stock_id = 1 -- 종목 id
            ORDER BY p.target_date \
            """
    df = pd.read_sql(query, db.bind)
    df.columns = ["date", "predicted", "actual"]
    buf = plot_prediction_graph(df)
    return Response(content=buf.getvalue(), media_type="image/png")


@router.get("/distribution/all")
def visualize_distribution_all(response: Response, db: Session = Depends(get_db)):
    """
    전체 종목의 예측 결과를 기반으로 오차율 분포 그래프 생성
    """
    query = """
            SELECT p.target_date, p.predicted_close, o.close
            FROM prediction p
                     JOIN stock_ohlcv_1d o
                          ON p.stock_id = o.stock_id
                              AND DATE (o.timestamp) = p.target_date
            WHERE o.timestamp BETWEEN '2025-08-06' AND '2025-10-28'
            ORDER BY p.target_date \
            """
    df = pd.read_sql(query, db.bind)
    df.columns = ["date", "predicted", "actual"]

    buf = plot_error_distribution(df)
    return Response(content=buf.getvalue(), media_type="image/png")
