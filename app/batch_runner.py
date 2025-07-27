import sys
import os
from datetime import datetime
from app.services.batch_service import BatchService

# 현재 경로가 어디든 app을 인식할 수 있도록 path 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 주말 체크
today = datetime.today()
if today.weekday() >= 5:  # 5: 토요일, 6: 일요일
    print("주말입니다. 배치 예측을 건너뜁니다.")
    sys.exit(0)

# TODO: 한국 공휴일 체크 추가 (원하면 API 연결하거나 날짜 하드코딩 가능)

# 배치 실행
print("배치 예측 시작")
BatchService.batch_predict_and_save(start_id=1, end_id=100, max_workers=2)
print("배치 예측 완료")
