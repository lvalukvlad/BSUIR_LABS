import time
from functools import wraps
from typing import Callable, Any
from .logger import logger

def measure_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(f"{func.__name__}: {elapsed:.2f}ms")
        return result
    return wrapper

def measure_time_verbose(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        logger.info(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(f"Completed {func.__name__} in {elapsed:.2f}ms")
        return result
    return wrapper