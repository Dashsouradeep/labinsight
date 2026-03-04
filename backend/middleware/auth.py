"""Authentication middleware for protecting routes.

This module provides middleware and dependency functions for validating JWT tokens
on protected routes, checking token blacklist in Redis, and extracting user information.

Requirements: 12.3
"""

from fastapi import HTTPException, status, Depends, Header
from typing import Optional
import logging

from services.auth_service import validate_token
from redis_client import redis_client

logger = logging.getLogger(__name__)


class AuthenticatedUser:
    """Container for authenticated user information extracted from JWT token."""
    
    def __init__(self, user_id: str, email: str):
        """Initialize authenticated user.
        
        Args:
            user_id: Unique identifier for the user
            email: User's email address
        """
        self.user_id = user_id
        self.email = email
    
    def __repr__(self) -> str:
        return f"AuthenticatedUser(user_id={self.user_id}, email={self.email})"


async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer token in format: Bearer <token>")
) -> AuthenticatedUser:
    """Dependency function to validate JWT token and extract user information.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Validates the token format and signature
    3. Checks if the token is blacklisted in Redis
    4. Extracts and returns user information from the token payload
    
    Args:
        authorization: Authorization header containing Bearer token
    
    Returns:
        AuthenticatedUser object containing user_id and email
    
    Raises:
        HTTPException 401: If token is missing, invalid, expired, or blacklisted
    
    Validates: Requirements 12.3
    """
    # Check if Authorization header is present
    if not authorization:
        logger.warning("Request to protected route without Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate Authorization header format
    if not authorization.startswith("Bearer "):
        logger.warning("Request with invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from Authorization header
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        logger.warning("Request with empty token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token signature and expiration
    payload = validate_token(token)
    if not payload:
        logger.warning("Request with invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token is blacklisted in Redis
    try:
        is_blacklisted = await redis_client.is_token_blacklisted(token)
        if is_blacklisted:
            logger.warning(
                "Request with blacklisted token",
                extra={
                    "user_id": payload.get("sub"),
                    "email": payload.get("email")
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Error checking token blacklist",
            extra={"error": str(e)}
        )
        # Fail closed for security - treat as blacklisted if Redis check fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to validate token. Please try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user information from token payload
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id or not email:
        logger.error(
            "Token payload missing required fields",
            extra={"payload": payload}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(
        "User authenticated successfully",
        extra={
            "user_id": user_id,
            "email": email
        }
    )
    
    return AuthenticatedUser(user_id=user_id, email=email)


# Convenience alias for use in route dependencies
CurrentUser = Depends(get_current_user)
