from apscheduler.schedulers.background import BackgroundScheduler
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.batch_service import BatchService
from app.utils.discord_notifier import notify_discord_async

logger = logging.getLogger(__name__)

@staticmethod
def start_batch_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    @scheduler.scheduled_job('cron', hour=18, minute=5)
    def run_batch():
        logger.info("[Scheduler] 18:05 배치 예측 시작")
        start = time.time()

        success_count = 0
        fail_count = 0
        failed_symbols = []

        start_id = 1
        end_id = 100
        max_workers = 8

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(BatchService.process_single_stock, stock_id): stock_id
                for stock_id in range(start_id, end_id + 1)
            }

            for future in as_completed(futures):
                stock_id = futures[future]
                try:
                    stock_id, success, symbol_or_msg = future.result()
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        failed_symbols.append(symbol_or_msg)  # symbol 저장
                except Exception as e:
                    logger.exception(f"[Batch] [{stock_id}] 처리 중 예외 발생: {str(e)}")
                    fail_count += 1

        duration = time.time() - start
        logger.info(
            f"[Scheduler] 배치 예측 완료 - 성공: {success_count}, 실패: {fail_count}, 소요 시간: {duration:.2f}s"
        )

        # event loop 중첩 방지용: asyncio.run 대신 loop 직접 생성
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                notify_discord_async(success_count, fail_count, duration, failed_symbols)
            )
        except Exception as e:
            logger.warning(f"디스코드 알림 실패: {e}")
        finally:
            loop.close()

    scheduler.start()
    logger.info("APScheduler 시작됨")
