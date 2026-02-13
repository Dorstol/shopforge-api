from typing import NoReturn

from fastapi import HTTPException, status
from sentry_sdk import capture_message


def log_exception(
    log_message: str, user_message: str = "General error, call support"
) -> NoReturn:
    capture_message(log_message, level="error")
    raise HTTPException(
        detail=user_message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
