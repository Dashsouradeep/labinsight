"""Example protected routes demonstrating authentication middleware usage.

This module provides example endpoints that demonstrate how to use the
authentication middleware to protect routes and access user information.

This is for demonstration purposes and can be removed in production.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from middleware.auth import get_current_user, AuthenticatedUser, CurrentUser

router = APIRouter(prefix="/api/example", tags=["example"])


class ProtectedResourceResponse(BaseModel):
    """Response model for protected resource."""
    message: str
    user_id: str
    email: str


class UserDataResponse(BaseModel):
    """Response model for user-specific data."""
    user_id: str
    email: str
    data: List[str]


@router.get(
    "/protected",
    response_model=ProtectedResourceResponse,
    summary="Example protected endpoint",
    description="Demonstrates basic authentication middleware usage."
)
async def get_protected_resource(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> ProtectedResourceResponse:
    """Example protected endpoint that requires authentication.
    
    This endpoint demonstrates:
    - How to use the get_current_user dependency
    - How to access authenticated user information
    - Automatic token validation and blacklist checking
    
    Args:
        current_user: Authenticated user information (injected by middleware)
    
    Returns:
        ProtectedResourceResponse with user information
    
    Raises:
        HTTPException 401: If token is missing, invalid, expired, or blacklisted
    """
    return ProtectedResourceResponse(
        message="Access granted to protected resource",
        user_id=current_user.user_id,
        email=current_user.email
    )


@router.get(
    "/user-data",
    response_model=UserDataResponse,
    summary="Example user-specific data endpoint",
    description="Demonstrates accessing user-specific data using CurrentUser alias."
)
async def get_user_data(
    current_user: AuthenticatedUser = CurrentUser
) -> UserDataResponse:
    """Example endpoint that returns user-specific data.
    
    This endpoint demonstrates:
    - Using the CurrentUser convenience alias
    - Filtering data based on authenticated user
    - Returning user-specific information
    
    Args:
        current_user: Authenticated user information (injected by middleware)
    
    Returns:
        UserDataResponse with user-specific data
    """
    # In a real application, you would query the database
    # using current_user.user_id to filter data
    user_specific_data = [
        f"Data item 1 for user {current_user.user_id}",
        f"Data item 2 for user {current_user.user_id}",
        f"Data item 3 for user {current_user.user_id}",
    ]
    
    return UserDataResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        data=user_specific_data
    )


@router.get(
    "/public",
    summary="Example public endpoint",
    description="Demonstrates an unprotected endpoint that doesn't require authentication."
)
async def get_public_resource():
    """Example public endpoint that doesn't require authentication.
    
    This endpoint demonstrates:
    - Routes without authentication middleware
    - Public access without token validation
    
    Returns:
        Dictionary with public message
    """
    return {
        "message": "This is a public endpoint, no authentication required",
        "access": "public"
    }
