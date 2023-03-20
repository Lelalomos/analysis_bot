from functools import wraps
import logging
import traceback

logger = logging.getLogger(__name__)

def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in function {func.__name__}: {e},\n Details:{traceback.format_exc()}")
    return wrapper