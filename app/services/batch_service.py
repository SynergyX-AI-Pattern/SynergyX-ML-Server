from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.stock import Stock
from app.models.stock_detail import StockDetail
from app.models.prediction import Prediction
import time
import datetime
from app.crud.prediction import create_prediction_objects, save_predictions
from app.services.prediction_service import PredictionService
import logging

logger = logging.getLogger(__name__)


class BatchService:
    """
    병렬 예측 + 저장 전용 서비스
    """

    @staticmethod
    def run_batch_in_chunks(start_id=1, end_id=100, chunk_size=20, max_workers=6, cooldown_sec=3):
        """
        종목 예측을 chunk 단위로 분할하여 순차적으로 실행합니다.

        Args:
            start_id (int): 시작 stock_id
            end_id (int): 종료 stock_id
            chunk_size (int): 한 번에 예측할 종목 수
            max_workers (int): 병렬 처리 최대 스레드 수
            cooldown_sec (int): 구간마다 대기 시간 (초)
        """
        logger.info(f"분할 배치 시작: {start_id} ~ {end_id} (chunk: {chunk_size})")

        success_count = 0
        fail_count = 0
        failed_symbols = []

        for start in range(start_id, end_id + 1, chunk_size):
            end = min(start + chunk_size - 1, end_id)

            logger.info(f"예측 구간: {start} ~ {end}")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(BatchService.process_single_stock, stock_id): stock_id
                    for stock_id in range(start, end + 1)
                }
                for future in as_completed(futures):
                    stock_id = futures[future]
                    try:
                        stock_id, success, symbol_or_msg = future.result()
                        if success:
                            success_count += 1
                        else:
                            fail_count += 1
                            failed_symbols.append(symbol_or_msg)
                    except Exception as e:
                        logger.exception(f"[{stock_id}] 처리 중 예외 발생: {str(e)}")
                        fail_count += 1

            if cooldown_sec > 0:
                time.sleep(cooldown_sec)

        logger.info("전체 분할 배치 완료")
        return success_count, fail_count, failed_symbols

    @staticmethod
    def process_single_stock(stock_id: int) -> tuple[int, bool, str]:
        """
        단일 종목 예측 및 저장 (독립 세션 사용, 실패해도 개별 처리)
        """
        db: Session = SessionLocal()

        try:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock:
                return stock_id, False, "종목 없음"

            symbol = stock.symbol
            logger.info(f"[{symbol}] 예측 시작")

            predictions = PredictionService.predict_15_days(symbol)

            prediction_objs = create_prediction_objects(stock_id, predictions)
            save_predictions(db, prediction_objs)

            logger.info(f"[{symbol}] 예측 및 저장 완료")
            return stock_id, True, "성공"

        except Exception as e:
            logger.exception(f"[{stock_id}] 예측 실패: {str(e)}")
            db.rollback()
            return stock_id, False, f"예외 발생: {str(e)}"

        finally:
            db.close()

    @staticmethod
    def batch_predict_and_save(start_id: int, end_id: int, max_workers: int = 2):
        """
        다수 종목 병렬 예측 및 저장 수행

        Args:
            start_id (int): 시작 stock_id
            end_id (int): 종료 stock_id
            max_workers (int): 동시에 처리할 최대 스레드 수
        """
        logger.info(f"배치 예측 시작: stock_id {start_id} ~ {end_id}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(BatchService.process_single_stock, stock_id): stock_id
                for stock_id in range(start_id, end_id + 1)
            }

            for future in as_completed(futures):
                stock_id = futures[future]
                try:
                    stock_id, success, message = future.result()
                    if success:
                        logger.info(f"[{stock_id}] 성공 - {message}")
                    else:
                        logger.warning(f"[{stock_id}] 실패 - {message}")
                except Exception as e:
                    logger.exception(f"[{stock_id}] 처리 중 예외 발생: {str(e)}")

        logger.info("전체 배치 완료")

    @staticmethod
    def update_ai_avg_increase_and_rank(base_date: datetime.date | None = None):
        """
        종목별 예측값 기반 실제 존재하는 예측일 기준 15일 평균 상승률 계산 후 stock_detail 업데이트
        :param base_date: 기준일 (None이면 오늘 날짜 사용)
        :return: None
        """
        db = SessionLocal()
        try:
            today = base_date or datetime.date.today()
            logger.info(f"[BatchService] 평균 상승률 계산 시작 (기준일: {today})")

            # --- 예측 데이터 존재 여부 확인 ---
            total_preds = db.query(Prediction).count()
            future_preds = db.query(Prediction).filter(Prediction.target_date > today).count()
            logger.info(f"[BatchService] Prediction 전체: {total_preds}건 / 기준일 이후: {future_preds}건")

            if future_preds == 0:
                logger.warning(f"[BatchService] 기준일({today}) 이후 예측 데이터가 없습니다.")
                return

            # --- 첫 번째 예측일 구하기 ---
            first_date_subq = (
                db.query(
                    Prediction.stock_id,
                    func.min(Prediction.target_date).label("first_target_date")
                )
                .filter(Prediction.target_date > today)
                .group_by(Prediction.stock_id)
                .subquery()
            )
            logger.debug(f"[BatchService] first_date_subq 생성 완료")

            # --- 첫 예측일의 예측 종가 구하기 ---
            subquery_first_price = (
                db.query(
                    Prediction.stock_id,
                    Prediction.predicted_close.label("first_predicted_close")
                )
                .join(
                    first_date_subq,
                    (Prediction.stock_id == first_date_subq.c.stock_id)
                    & (Prediction.target_date == first_date_subq.c.first_target_date)
                )
                .subquery()
            )
            first_price_count = db.query(subquery_first_price).count()
            logger.info(f"[BatchService] 첫 예측일 종가 매핑 완료 ({first_price_count}건)")

            # --- 평균 상승률 계산 ---
            results = (
                db.query(
                    Prediction.stock_id,
                    func.avg(
                        (Prediction.predicted_close - subquery_first_price.c.first_predicted_close)
                        / func.nullif(subquery_first_price.c.first_predicted_close, 0.0)
                    ).label("avg_increase")
                )
                .join(subquery_first_price, Prediction.stock_id == subquery_first_price.c.stock_id)
                .filter(Prediction.target_date > today)
                .group_by(Prediction.stock_id)
                .all()
            )

            logger.info(f"[BatchService] 평균 상승률 계산 결과: {len(results)}건")

            if not results:
                logger.warning("[BatchService] 평균 상승률 계산 결과 없음 (JOIN 또는 데이터 매칭 문제 가능)")
                return

            # --- 상위 3개 샘플 출력 ---
            sample_logs = [
                f"stock_id={r.stock_id}, avg_increase={round((r.avg_increase or 0) * 100, 2)}%"
                for r in results[:3]
            ]
            logger.debug(f"[BatchService] 계산 결과 샘플: {sample_logs}")

            # --- 평균 상승률 내림차순 정렬 및 랭킹 부여 ---
            sorted_results = sorted(results, key=lambda r: r.avg_increase or 0, reverse=True)

            for rank, row in enumerate(sorted_results, start=1):
                db.query(StockDetail).filter(StockDetail.stock_id == row.stock_id).update(
                    {
                        StockDetail.ai_avg_increase: row.avg_increase,
                        StockDetail.ai_rank: rank,
                        StockDetail.updated_at: datetime.datetime.utcnow(),
                    }
                )
                if rank <= 3:  # 상위 3개만 출력
                    logger.debug(
                        f"[BatchService] UPDATE → stock_id={row.stock_id}, "
                        f"avg_increase={row.avg_increase}, rank={rank}"
                    )

            db.commit()
            logger.info(f"[BatchService] 평균 상승률 및 랭킹 갱신 완료 ({len(sorted_results)}개 종목)")

            # 상위 3개 종목 조회
            top3 = (
                db.query(Stock.name, StockDetail.ai_avg_increase)
                .join(StockDetail, Stock.id == StockDetail.stock_id)
                .order_by(StockDetail.ai_rank.asc())
                .limit(3)
                .all()
            )

            # 디스코드 알림용 리스트 반환
            top3_info = [
                {"name": name, "increase": round((increase or 0) * 100, 2)}
                for name, increase in top3
            ]

            return top3_info

        except Exception as e:
            db.rollback()
            logger.exception(f"[BatchService] 평균 상승률 계산 중 오류 발생: {e}")
            raise

        finally:
            db.close()
            logger.debug("[BatchService] 세션 종료 완료")
