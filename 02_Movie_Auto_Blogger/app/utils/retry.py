"""Retry policy utilities with exponential backoff and jitter."""
import asyncio
import random
import time
from typing import Callable, TypeVar, Tuple, Optional
from app.utils.logging import get_logger

logger = get_logger("retry_policy")

T = TypeVar("T")

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def is_retryable_error(exception: Exception) -> bool:
    """Classify whether an exception is temporary and eligible for retry."""
    err_str = str(exception).lower()
    if any(term in err_str for term in ["timeout", "connection reset", "temporarily unavailable", "rate limit", "429"]):
        return True

    # Check for HTTP status code in exception if available
    status_code = getattr(exception, "status_code", None) or getattr(exception, "code", None)
    if status_code and status_code in RETRYABLE_STATUS_CODES:
        return True

    return False


async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
) -> T:
    """Execute an async function with exponential backoff for retryable exceptions."""
    attempt = 1
    delay = initial_delay

    while True:
        try:
            return await func()
        except Exception as e:
            if attempt >= max_attempts or not is_retryable_error(e):
                logger.error("Operation failed permanently after %d attempt(s): %s", attempt, str(e))
                raise e

            sleep_time = delay + (random.uniform(0.1, 0.5) if jitter else 0.0)
            logger.warning("Attempt %d failed (%s). Retrying in %.2fs...", attempt, str(e), sleep_time)
            await asyncio.sleep(sleep_time)

            attempt += 1
            delay *= backoff_factor
