"""Utility modules for error handling, retry logic, and circuit breakers."""

from .error_handling import (
    ErrorResponse,
    ErrorDetail,
    LabInsightError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ProcessingError,
    ServiceUnavailableError,
    RateLimitError,
    format_error_response,
    map_exception_to_response,
    labinsight_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

from .retry_logic import (
    RetryConfig,
    retry_sync,
    retry_async,
    retry_ocr,
    retry_ner,
    retry_llm,
    retry_db_async,
    retry_db_sync,
)

from .circuit_breaker import (
    CircuitState,
    CircuitBreaker,
    CircuitBreakerError,
    get_circuit_breaker,
    get_ocr_circuit_breaker,
    get_ner_circuit_breaker,
    get_llm_circuit_breaker,
    circuit_breaker,
)

__all__ = [
    # Error handling
    "ErrorResponse",
    "ErrorDetail",
    "LabInsightError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ProcessingError",
    "ServiceUnavailableError",
    "RateLimitError",
    "format_error_response",
    "map_exception_to_response",
    "labinsight_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "generic_exception_handler",
    # Retry logic
    "RetryConfig",
    "retry_sync",
    "retry_async",
    "retry_ocr",
    "retry_ner",
    "retry_llm",
    "retry_db_async",
    "retry_db_sync",
    # Circuit breaker
    "CircuitState",
    "CircuitBreaker",
    "CircuitBreakerError",
    "get_circuit_breaker",
    "get_ocr_circuit_breaker",
    "get_ner_circuit_breaker",
    "get_llm_circuit_breaker",
    "circuit_breaker",
]
