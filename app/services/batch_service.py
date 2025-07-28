from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.stock import Stock
import time
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

        for start in range(start_id, end_id + 1, chunk_size):
            end = min(start + chunk_size - 1, end_id)

            logger.info(f"예측 구간: {start} ~ {end}")
            BatchService.batch_predict_and_save(start_id=start, end_id=end, max_workers=max_workers)

            if cooldown_sec > 0:
                time.sleep(cooldown_sec)

        logger.info("전체 분할 배치 완료")

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
