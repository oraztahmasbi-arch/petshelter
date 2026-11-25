import logging
from functools import wraps
from time import perf_counter
from typing import Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def log_operation(func: Callable[P, R]) -> Callable[P, R]:
    """Log the start, completion, and failure of an operation."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("Starting operation: %s", func.__qualname__)
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.exception("Operation failed: %s", func.__qualname__)
            raise
        logger.info("Operation completed: %s", func.__qualname__)
        return result

    return wrapper


def execution_time(func: Callable[P, R]) -> Callable[P, R]:
    """Log the execution time of an operation, including failed calls."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            logger.info("%s executed in %.6f seconds", func.__qualname__, elapsed)

    return wrapper
