import logging
import sys
from app.core.config import settings

LOG_FORMAT = "[%(levelname)s] %(asctime)s | %(name)s | %(message)s"
LOG_LEVEL = logging.DEBUG if settings.ENV == "local" else logging.INFO

def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        stream=sys.stdout,
    )
