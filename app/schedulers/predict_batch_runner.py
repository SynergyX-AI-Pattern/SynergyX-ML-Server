from apscheduler.schedulers.background import BackgroundScheduler
import logging
import time
import asyncio
from app.services.batch_service import BatchService
from app.utils.discord_notifier import notify_discord_async

logger = logging.getLogger(__name__)


def start_batch_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    @scheduler.scheduled_job(
        'cron',
        hour=16, minute=5, day_of_week='mon-fri',
        coalesce=False,  # 밀린 작업 버림
        max_instances=1,  # 중복 실행 방지
        misfire_grace_time=600  # 지연 허용 10분
    )
    def run_batch():
        logger.info("[Scheduler] 16:05 배치 예측 시작")
        start_time = time.time()

        start_id, end_id = 1, 100
        chunk_size = 20
        max_workers = 6
        cooldown_sec = 2

        success_count, fail_count, failed_symbols = BatchService.run_batch_in_chunks(
            start_id=start_id,
            end_id=end_id,
            chunk_size=chunk_size,
            max_workers=max_workers,
            cooldown_sec=cooldown_sec
        )

        duration = time.time() - start_time
        logger.info(
            f"[Scheduler] 배치 예측 완료 - 성공: {success_count}, 실패: {fail_count}, 소요: {duration:.2f}s"
        )

        # Discord 알림
        # 스레드에서 비동기 함수 실행
        try:
            import threading
            def run_notification():
                asyncio.run(
                    notify_discord_async(success_count, fail_count, duration, failed_symbols, 1404342496221462539))

            notification_thread = threading.Thread(target=run_notification)
            notification_thread.start()
            notification_thread.join(timeout=30)  # 30초 타임아웃
        except Exception as e:
            logger.warning(f"디스코드 알림 실패: {e}")

    scheduler.start()
    logger.info("APScheduler 시작됨")
