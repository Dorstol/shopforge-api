import logging
import sys

from logtail import LogtailHandler
from settings import settings


def get_betterstack_logger():
    handler = LogtailHandler(
        source_token=settings.BETTER_STACK_TOKEN,
        host=settings.BETTER_STACK_HOST,
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(handler)

    stream_heandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream_heandler.setFormatter(formatter)
    logger.addHandler(stream_heandler)
    return logger


betterstack_logger = get_betterstack_logger()
