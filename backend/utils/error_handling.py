"""
Error Handling Utilities

Provides consistent error response formatting, exception mapping,
and error handling utilities for the LabInsight platform.

Requirements: 12.4, 17.1-17.7
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


# Error Response Models

class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    message: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """Consistent error response structure.
    
    Requirements: 12.4, 17.1
    """
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime
    request_id: Optional[str] = None


# Custom Exception Classes

class LabInsightError(Exception):
    """Base exception for LabInsight application errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[Dict[str, Any]]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(self.message)


class ValidationError(LabInsightError):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class AuthenticationError(LabInsightError):
    """Authentication error exception."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(LabInsightError):
    """Authorization error exception."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(LabInsightError):
    """Resource not found error exception."""
    
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} not found",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=[{"field": "id", "message": f"{resource} with ID {resource_id} not found"}]
        )


class ProcessingError(LabInsightError):
    """Processing error exception."""
    
    def __init__(self, message: str, stage: Optional[str] = None):
        details = [{"field": "stage", "message": stage}] if stage else None
        super().__init__(
            message=message,
            code="PROCESSING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ServiceUnavailableError(LabInsightError):
    """Service unavailable error exception."""
    
    def __init__(self, service: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"{service} is currently unavailable",
            code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=[{"field": "service", "message": service}]
        )


class RateLimitError(LabInsightError):
    """Rate limit exceeded error exception."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


# Error Response Formatting

def format_error_response(
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format error response with consistent structure.
    
    Requirements: 12.4, 17.1
    
    Args:
        code: Error code
        message: Error message
        details: Optional error details
        request_id: Optional request ID for tracking
        
    Returns:
        Formatted error response dictionary
    """
    error_details = None
    if details:
        error_details = [
            ErrorDetail(
                field=d.get("field"),
                message=d.get("message", ""),
                type=d.get("type")
            )
            for d in details
        ]
    
    response = ErrorResponse(
        code=code,
        message=message,
        details=error_details,
        timestamp=datetime.utcnow(),
        request_id=request_id
    )
    
    return response.model_dump(exclude_none=True)


def map_exception_to_response(
    exc: Exception,
    request_id: Optional[str] = None
) -> tuple[int, Dict[str, Any]]:
    """
    Map exceptions to HTTP status codes and error responses.
    
    Requirements: 12.4, 17.1
    
    Args:
        exc: Exception to map
        request_id: Optional request ID
        
    Returns:
        Tuple of (status_code, error_response)
    """
    # LabInsight custom exceptions
    if isinstance(exc, LabInsightError):
        return exc.status_code, format_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id
        )
    
    # FastAPI HTTPException
    if isinstance(exc, HTTPException):
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
            503: "SERVICE_UNAVAILABLE"
        }
        
        return exc.status_code, format_error_response(
            code=code_map.get(exc.status_code, "HTTP_ERROR"),
            message=exc.detail,
            request_id=request_id
        )
    
    # Validation errors
    if isinstance(exc, RequestValidationError):
        details = []
        for error in exc.errors():
            details.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return status.HTTP_422_UNPROCESSABLE_ENTITY, format_error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=details,
            request_id=request_id
        )
    
    # Generic exceptions
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return status.HTTP_500_INTERNAL_SERVER_ERROR, format_error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        request_id=request_id
    )


# Exception Handlers

async def labinsight_exception_handler(request: Request, exc: LabInsightError) -> JSONResponse:
    """Handle LabInsight custom exceptions."""
    status_code, error_response = map_exception_to_response(exc)
    
    logger.error(
        f"LabInsight error: {exc.code}",
        extra={
            "code": exc.code,
            "message": exc.message,
            "status_code": status_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    status_code, error_response = map_exception_to_response(exc)
    
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    status_code, error_response = map_exception_to_response(exc)
    
    logger.warning(
        "Validation error",
        extra={
            "errors": exc.errors(),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    status_code, error_response = map_exception_to_response(exc)
    
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )
