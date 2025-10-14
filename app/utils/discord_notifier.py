import os
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    parts = []
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if remaining_seconds or not parts:
        parts.append(f"{remaining_seconds}초")

    return " ".join(parts)


async def notify_discord_async(
        success_count: int,
        fail_count: int,
        duration: float,
        failed_symbols: list[str] = None,
        mention_role_id: str = None,
        top3_info: list[dict] = None,
) -> None:
    """
    배치 예측 결과를 디스코드로 전송하는 비동기 함수
    """
    import os
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")
        return

    total = success_count + fail_count
    formatted_duration = format_duration(duration)
    today_str = datetime.now().strftime('%Y-%m-%d')

    # 역할 멘션 문자열 생성
    mention_str = f"<@&{mention_role_id}> " if mention_role_id else ""

    content = f"""
{mention_str}📊 배치 예측 완료 ({today_str})
- 종목 수: {total}
- 성공: {success_count}
- 실패: {fail_count}
- 소요 시간: {formatted_duration}
    """.strip()

    # 실패 종목이 존재하면 추가
    if fail_count > 0 and failed_symbols:
        symbol_list = ", ".join(failed_symbols)
        content += f"\n- 실패 종목: {symbol_list}"

    # top 3 종목 문자열 생성
    if top3_info:
        top3_text = "\n".join(
            [f"{i + 1}위: {item['name']} (+{item['increase']}%)" for i, item in enumerate(top3_info)]
        )
        content += f"\n\n🔥 **Top 3**\n{top3_text}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                DISCORD_WEBHOOK_URL,
                json={"content": content}
            )

            if response.status_code != 204:
                logger.warning(
                    f"디스코드 알림 실패 - 상태코드: {response.status_code}, 응답: {response.text}"
                )
            else:
                logger.info("디스코드 알림 전송 성공")

    except httpx.RequestError as e:
        logger.warning(f"디스코드 요청 중 오류 발생: {str(e)}")

    except Exception as e:
        logger.exception("디스코드 알림 중 예기치 못한 예외 발생")
