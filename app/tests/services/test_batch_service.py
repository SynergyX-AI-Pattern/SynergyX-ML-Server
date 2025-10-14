import os
import datetime
from dotenv import load_dotenv
import logging

# --- FastAPI와 동일한 로깅 설정 불러오기 ---
from app.core.logging_config import setup_logging
setup_logging()

# --- 환경 변수 로드 ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

from app.db.session import SessionLocal
from app.services.batch_service import BatchService


def test_update_ai_avg_increase_and_rank_real_db():
    """
    [통합테스트] 실제 DB 기준으로 평균 상승률 계산 및 stock_detail 업데이트 테스트
    """
    db = SessionLocal()

    # 테스트용 기준일 (직접 지정 가능)
    base_date = datetime.date(2025, 10, 13)

    print(f"[TEST] 기준일: {base_date}")

    try:
        BatchService.update_ai_avg_increase_and_rank(base_date)
        db.commit()
        print("[SUCCESS] 평균 상승률 갱신 완료")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] 테스트 중 예외 발생: {e}")
        raise

    finally:
        db.close()
