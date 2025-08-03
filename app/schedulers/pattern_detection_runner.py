from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.pattern_detection_service import PatternDetectionService
import logging

logger = logging.getLogger(__name__)

def run_realtime_detection_job():
    db: Session = SessionLocal()
    try:
        PatternDetectionService.detect(db)
    except Exception as e:
        logger.exception(f"[패턴 감지 스케줄러] 감지 실행 중 예외 발생: {e}")
    finally:
        db.close()

def start_pattern_detection_scheduler():

    """
    월요일 ~ 금요일 (9:00 ~ 15:45) 15분 간격으로 패턴 감지를 수행합니다.
    Returns:
        BackgroundScheduler: 시작된 스케줄러 인스턴스
    """

    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    scheduler.add_job(
        run_realtime_detection_job,
        CronTrigger(
            minute="0,15,30,45",
            hour="9-15",
            day_of_week="mon-fri"
        ),
        id="realtime_pattern_detection",
        name="실시간 패턴 감지 스케줄러",
        replace_existing=True
    )

    logging.info("[패턴 감지 스케줄러] 실시간 감지 시작")
    scheduler.start()
    return scheduler
