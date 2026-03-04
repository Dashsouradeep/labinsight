"""Authentication API routes for user registration and login.

This module provides endpoints for user authentication including:
- POST /api/auth/signup - User registration
- POST /api/auth/login - User authentication
- POST /api/auth/logout - Session termination

Requirements: 1.1, 1.2, 1.3, 1.4, 1.7, 15.1, 15.2, 15.3
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re
import logging

from models.schemas import User, UserProfile
from services.auth_service import hash_password, verify_password, generate_token, validate_token, get_token_expiration
from database import get_database
from redis_client import redis_client
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models

class SignupRequest(BaseModel):
    """Request model for user registration.
    
    Validates: Requirements 1.1, 15.1
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password (min 8 characters)")
    age: int = Field(..., ge=0, le=150, description="User's age in years")
    gender: str = Field(..., description="User's gender (male, female, other)")
    name: Optional[str] = Field(None, description="User's name (optional)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength.
        
        Password must contain:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        
        return v
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender value."""
        if v.lower() not in ['male', 'female', 'other']:
            raise ValueError("Gender must be 'male', 'female', or 'other'")
        return v.lower()


class SignupResponse(BaseModel):
    """Response model for user registration.
    
    Validates: Requirements 1.1, 15.1
    """
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="Success message")


class LoginRequest(BaseModel):
    """Request model for user login.
    
    Validates: Requirements 1.3, 15.2
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User password")


class UserProfileResponse(BaseModel):
    """User profile information for response."""
    id: str
    email: str
    age: int
    gender: str
    name: Optional[str] = None


class LoginResponse(BaseModel):
    """Response model for user login.
    
    Validates: Requirements 1.3, 15.2
    """
    token: str = Field(..., description="JWT authentication token")
    user: UserProfileResponse = Field(..., description="User profile information")


class LogoutResponse(BaseModel):
    """Response model for user logout.
    
    Validates: Requirements 1.7, 15.3
    """
    message: str = Field(..., description="Logout confirmation message")


# API Endpoints

@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password. Validates email format and password strength.",
)
async def signup(
    request: SignupRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> SignupResponse:
    """Create a new user account.
    
    This endpoint:
    1. Validates email format and password strength
    2. Checks for duplicate emails
    3. Hashes the password using bcrypt with cost factor 12
    4. Stores the user in the database
    
    Args:
        request: SignupRequest containing email, password, age, gender, and optional name
        db: MongoDB database instance (injected)
    
    Returns:
        SignupResponse with user_id and success message
    
    Raises:
        HTTPException 400: If email already exists or validation fails
        HTTPException 500: If database operation fails
    
    Validates: Requirements 1.1, 1.2, 15.1
    """
    try:
        # Check for duplicate email
        existing_user = await db.users.find_one({"email": request.email})
        if existing_user:
            logger.warning(
                "Signup attempt with existing email",
                extra={"email": request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists"
            )
        
        # Hash the password
        password_hash = hash_password(request.password)
        
        # Create user profile
        profile = UserProfile(
            age=request.age,
            gender=request.gender,
            name=request.name
        )
        
        # Create user document
        user = User(
            email=request.email,
            password_hash=password_hash,
            profile=profile,
            terms_accepted=True,  # Assuming terms are accepted during signup
            terms_accepted_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Insert user into database
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await db.users.insert_one(user_dict)
        
        user_id = str(result.inserted_id)
        
        logger.info(
            "User registered successfully",
            extra={
                "user_id": user_id,
                "email": request.email
            }
        )
        
        return SignupResponse(
            user_id=user_id,
            message="User account created successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Error during user registration",
            extra={
                "email": request.email,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again."
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT token",
    description="Verify user credentials and return a JWT token with 24-hour expiration.",
)
async def login(
    request: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> LoginResponse:
    """Authenticate user and issue JWT token.
    
    This endpoint:
    1. Validates email and password
    2. Verifies credentials against stored user data
    3. Issues a JWT token with 24-hour expiration on success
    
    Args:
        request: LoginRequest containing email and password
        db: MongoDB database instance (injected)
    
    Returns:
        LoginResponse with JWT token and user profile
    
    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 500: If database operation fails
    
    Validates: Requirements 1.3, 1.4, 15.2
    """
    try:
        # Find user by email
        user_doc = await db.users.find_one({"email": request.email})
        
        if not user_doc:
            logger.warning(
                "Login attempt with non-existent email",
                extra={"email": request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user_doc["password_hash"]):
            logger.warning(
                "Login attempt with incorrect password",
                extra={"email": request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token
        user_id = str(user_doc["_id"])
        token = generate_token(user_id, request.email)
        
        # Create user profile response
        profile = user_doc.get("profile", {})
        user_profile = UserProfileResponse(
            id=user_id,
            email=user_doc["email"],
            age=profile.get("age", 0),
            gender=profile.get("gender", "other"),
            name=profile.get("name")
        )
        
        logger.info(
            "User logged in successfully",
            extra={
                "user_id": user_id,
                "email": request.email
            }
        )
        
        return LoginResponse(
            token=token,
            user=user_profile
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Error during user login",
            extra={
                "email": request.email,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )



@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user and invalidate session token",
    description="Invalidate the user's session token by adding it to the Redis blacklist.",
)
async def logout(
    authorization: str = Header(..., description="Bearer token in format: Bearer <token>")
) -> LogoutResponse:
    """Logout user and invalidate session token.
    
    This endpoint:
    1. Extracts the JWT token from the Authorization header
    2. Validates the token
    3. Adds the token to Redis blacklist with TTL matching token expiration
    4. Returns success confirmation
    
    Args:
        authorization: Authorization header containing Bearer token
    
    Returns:
        LogoutResponse with success message
    
    Raises:
        HTTPException 401: If token is missing, invalid, or malformed
        HTTPException 500: If Redis operation fails
    
    Validates: Requirements 1.7, 15.3
    """
    try:
        # Extract token from Authorization header
        # Expected format: "Bearer <token>"
        if not authorization.startswith("Bearer "):
            logger.warning("Logout attempt with invalid Authorization header format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected: Bearer <token>"
            )
        
        token = authorization[7:]  # Remove "Bearer " prefix
        
        if not token:
            logger.warning("Logout attempt with empty token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is required"
            )
        
        # Validate token
        payload = validate_token(token)
        if not payload:
            logger.warning("Logout attempt with invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get token expiration to set appropriate TTL in Redis
        expiration = get_token_expiration(token)
        if not expiration:
            logger.error("Failed to get token expiration")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process logout"
            )
        
        # Calculate remaining time until token expires
        now = datetime.now(expiration.tzinfo)
        remaining_seconds = int((expiration - now).total_seconds())
        
        # Only blacklist if token hasn't expired yet
        if remaining_seconds > 0:
            await redis_client.blacklist_token(token, remaining_seconds)
            logger.info(
                "User logged out successfully",
                extra={
                    "user_id": payload.get("sub"),
                    "email": payload.get("email")
                }
            )
        else:
            # Token already expired, no need to blacklist
            logger.info(
                "Logout with already expired token",
                extra={
                    "user_id": payload.get("sub"),
                    "email": payload.get("email")
                }
            )
        
        return LogoutResponse(
            message="Logged out successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Error during logout",
            extra={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout. Please try again."
        )
