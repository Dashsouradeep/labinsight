"""
Circuit Breaker Pattern Implementation

Provides circuit breaker functionality for AI models to prevent
cascading failures and allow graceful degradation.

Requirements: 17.1-17.7
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Callable, Optional, Any, TypeVar
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for service resilience.
    
    Requirements: 17.1-17.7
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing recovery, limited requests allowed
    
    Configuration:
    - failure_threshold: Number of consecutive failures before opening
    - recovery_timeout: Seconds to wait before attempting recovery
    - success_threshold: Successful requests needed to close from half-open
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker name for logging
            failure_threshold: Consecutive failures before opening circuit
            recovery_timeout: Seconds to wait before half-open state
            success_threshold: Successes needed to close from half-open
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self._state == CircuitState.HALF_OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return False
        
        elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    async def _transition_to_open(self):
        """Transition circuit to OPEN state."""
        async with self._lock:
            self._state = CircuitState.OPEN
            self._last_failure_time = datetime.utcnow()
            
            logger.warning(
                f"Circuit breaker '{self.name}' opened",
                extra={
                    "circuit": self.name,
                    "state": "OPEN",
                    "failure_count": self._failure_count,
                    "recovery_timeout": self.recovery_timeout
                }
            )
    
    async def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state."""
        async with self._lock:
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0
            
            logger.info(
                f"Circuit breaker '{self.name}' half-open (testing recovery)",
                extra={
                    "circuit": self.name,
                    "state": "HALF_OPEN"
                }
            )
    
    async def _transition_to_closed(self):
        """Transition circuit to CLOSED state."""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            
            logger.info(
                f"Circuit breaker '{self.name}' closed (recovered)",
                extra={
                    "circuit": self.name,
                    "state": "CLOSED"
                }
            )
    
    async def record_success(self):
        """Record a successful operation."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                
                if self._success_count >= self.success_threshold:
                    await self._transition_to_closed()
            
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0
    
    async def record_failure(self):
        """Record a failed operation."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                # Failed during recovery test, reopen circuit
                await self._transition_to_open()
            
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                
                if self._failure_count >= self.failure_threshold:
                    await self._transition_to_open()
    
    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check if we should attempt reset
        if self._state == CircuitState.OPEN and self._should_attempt_reset():
            await self._transition_to_half_open()
        
        # Fail fast if circuit is open
        if self._state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Service unavailable, will retry in {self.recovery_timeout}s"
            )
        
        # Attempt to call function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self.record_success()
            return result
            
        except Exception as e:
            await self.record_failure()
            raise
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        
        logger.info(
            f"Circuit breaker '{self.name}' manually reset",
            extra={"circuit": self.name, "state": "CLOSED"}
        )


# Global circuit breakers for AI services

_circuit_breakers = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 2
) -> CircuitBreaker:
    """
    Get or create a circuit breaker instance.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        recovery_timeout: Seconds before retry
        success_threshold: Successes to close
        
    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold
        )
    
    return _circuit_breakers[name]


# Predefined circuit breakers for AI services

def get_ocr_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for OCR service."""
    return get_circuit_breaker(
        name="ocr_service",
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=2
    )


def get_ner_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for NER service."""
    return get_circuit_breaker(
        name="ner_service",
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=2
    )


def get_llm_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for LLM service."""
    return get_circuit_breaker(
        name="llm_service",
        failure_threshold=5,
        recovery_timeout=60.0,
        success_threshold=2
    )


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 2
):
    """
    Decorator to wrap functions with circuit breaker.
    
    Requirements: 17.1-17.7
    
    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        recovery_timeout: Seconds before retry
        success_threshold: Successes to close
        
    Example:
        @circuit_breaker(name="my_service", failure_threshold=5)
        async def my_function():
            # Function that might fail
            pass
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        breaker = get_circuit_breaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold
        )
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            return await breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator
