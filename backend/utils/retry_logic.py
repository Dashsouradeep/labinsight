"""
Retry Logic with Exponential Backoff

Provides retry decorators and utilities for handling transient failures
in OCR, NER, LLM, and database operations.

Requirements: 17.1-17.7
"""

import asyncio
import logging
import time
from typing import TypeVar, Callable, Optional, Type, Tuple, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    # OCR failures: 3 retries (1s, 2s, 4s)
    OCR_MAX_RETRIES = 3
    OCR_INITIAL_DELAY = 1.0
    OCR_BACKOFF_FACTOR = 2.0
    OCR_MAX_DELAY = 4.0
    
    # NER failures: 3 retries
    NER_MAX_RETRIES = 3
    NER_INITIAL_DELAY = 1.0
    NER_BACKOFF_FACTOR = 2.0
    NER_MAX_DELAY = 4.0
    
    # LLM timeouts: 2 retries
    LLM_MAX_RETRIES = 2
    LLM_INITIAL_DELAY = 2.0
    LLM_BACKOFF_FACTOR = 2.0
    LLM_MAX_DELAY = 8.0
    
    # Database errors: 5 retries
    DB_MAX_RETRIES = 5
    DB_INITIAL_DELAY = 0.5
    DB_BACKOFF_FACTOR = 2.0
    DB_MAX_DELAY = 10.0


def calculate_delay(
    attempt: int,
    initial_delay: float,
    backoff_factor: float,
    max_delay: float
) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Current attempt number (1-indexed)
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay cap
        
    Returns:
        Delay in seconds
    """
    delay = initial_delay * (backoff_factor ** (attempt - 1))
    return min(delay, max_delay)


def retry_sync(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 10.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for synchronous functions with retry logic.
    
    Requirements: 17.1-17.7
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay before first retry
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay between retries
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
        
    Example:
        @retry_sync(max_retries=3, initial_delay=1.0)
        def my_function():
            # Function that might fail
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt >= max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": max_retries,
                                "error": str(e)
                            }
                        )
                        raise
                    
                    delay = calculate_delay(attempt, initial_delay, backoff_factor, max_delay)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed, retrying in {delay}s",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_retries": max_retries,
                            "delay": delay,
                            "error": str(e)
                        }
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def retry_async(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 10.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for asynchronous functions with retry logic.
    
    Requirements: 17.1-17.7
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay before first retry
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay between retries
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
        
    Example:
        @retry_async(max_retries=3, initial_delay=1.0)
        async def my_async_function():
            # Async function that might fail
            pass
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt >= max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": max_retries,
                                "error": str(e)
                            }
                        )
                        raise
                    
                    delay = calculate_delay(attempt, initial_delay, backoff_factor, max_delay)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed, retrying in {delay}s",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_retries": max_retries,
                            "delay": delay,
                            "error": str(e)
                        }
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    await asyncio.sleep(delay)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


# Predefined retry decorators for specific services

def retry_ocr(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry decorator for OCR operations.
    
    OCR failures: 3 retries (1s, 2s, 4s)
    Requirements: 17.1-17.7
    """
    return retry_sync(
        max_retries=RetryConfig.OCR_MAX_RETRIES,
        initial_delay=RetryConfig.OCR_INITIAL_DELAY,
        backoff_factor=RetryConfig.OCR_BACKOFF_FACTOR,
        max_delay=RetryConfig.OCR_MAX_DELAY,
        exceptions=(Exception,)
    )(func)


def retry_ner(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry decorator for NER operations.
    
    NER failures: 3 retries
    Requirements: 17.1-17.7
    """
    return retry_sync(
        max_retries=RetryConfig.NER_MAX_RETRIES,
        initial_delay=RetryConfig.NER_INITIAL_DELAY,
        backoff_factor=RetryConfig.NER_BACKOFF_FACTOR,
        max_delay=RetryConfig.NER_MAX_DELAY,
        exceptions=(Exception,)
    )(func)


def retry_llm(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry decorator for LLM operations.
    
    LLM timeouts: 2 retries
    Requirements: 17.1-17.7
    """
    return retry_sync(
        max_retries=RetryConfig.LLM_MAX_RETRIES,
        initial_delay=RetryConfig.LLM_INITIAL_DELAY,
        backoff_factor=RetryConfig.LLM_BACKOFF_FACTOR,
        max_delay=RetryConfig.LLM_MAX_DELAY,
        exceptions=(Exception,)
    )(func)


def retry_db_async(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Retry decorator for async database operations.
    
    Database errors: 5 retries
    Requirements: 17.1-17.7
    """
    return retry_async(
        max_retries=RetryConfig.DB_MAX_RETRIES,
        initial_delay=RetryConfig.DB_INITIAL_DELAY,
        backoff_factor=RetryConfig.DB_BACKOFF_FACTOR,
        max_delay=RetryConfig.DB_MAX_DELAY,
        exceptions=(Exception,)
    )(func)


def retry_db_sync(func: Callable[..., T]) -> Callable[..., T]:
    """
    Retry decorator for sync database operations.
    
    Database errors: 5 retries
    Requirements: 17.1-17.7
    """
    return retry_sync(
        max_retries=RetryConfig.DB_MAX_RETRIES,
        initial_delay=RetryConfig.DB_INITIAL_DELAY,
        backoff_factor=RetryConfig.DB_BACKOFF_FACTOR,
        max_delay=RetryConfig.DB_MAX_DELAY,
        exceptions=(Exception,)
    )(func)
