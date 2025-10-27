import requests

from app.api_payload.code.error_status import ErrorStatus
from app.core.config import settings
from app.exceptions.base import APIException

def send_notification_to_spring(user_id: int, title: str, message: str, notification_type: str):
    """
    SpringBoot 서버로 알림을 전송하는 유틸 함수입니다.
    """
    base_url = settings.SPRING_SERVER_BASE_URL
    url = f"{base_url}/test/notifications/send"
    payload = {
        "userId": user_id,
        "title": title,
        "message": message,
        "type": notification_type
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise APIException(ErrorStatus.NOTIFICATION_SEND_FAILED) from e
