"""Authentication service for user management and password hashing.

This module provides password hashing and verification using bcrypt with cost factor 12,
as specified in Requirement 13.7. It also provides JWT token generation and validation
with 24-hour expiration as specified in Requirement 1.6.
"""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import time

from config import settings


# JWT Configuration
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
TOKEN_EXPIRATION_HOURS = settings.jwt_expiration_hours


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with cost factor 12.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password as a string
        
    Validates: Requirements 13.7
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt with cost factor 12 and hash the password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Validates: Requirements 13.7
    """
    # Convert both to bytes
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Verify password
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def generate_token(user_id: str, email: str) -> str:
    """Generate a JWT token with 24-hour expiration.
    
    Args:
        user_id: Unique identifier for the user
        email: User's email address
        
    Returns:
        JWT token as a string
        
    Validates: Requirements 1.6
    """
    # Get current time in UTC
    now = datetime.now(timezone.utc)
    
    # Calculate expiration time (24 hours from now)
    expiration = now + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    
    # Create token payload with high-precision timestamp
    payload = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "exp": expiration,  # Expiration time
        "iat": now  # Issued at time
    }
    
    # Generate and return JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def validate_token(token: str) -> Optional[dict]:
    """Validate a JWT token and return the payload if valid.
    
    Args:
        token: JWT token string to validate
        
    Returns:
        Dictionary containing token payload if valid, None if invalid or expired
        
    Validates: Requirements 1.6
    """
    try:
        # Decode and validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired (jwt.decode already checks this, but being explicit)
        expiration = payload.get("exp")
        if expiration is None:
            return None
            
        # Return payload if valid
        return payload
        
    except JWTError:
        # Token is invalid, expired, or malformed
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """Get the expiration time from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Datetime object representing expiration time (UTC), or None if token is invalid
        
    Validates: Requirements 1.6
    """
    payload = validate_token(token)
    if payload is None:
        return None
    
    exp_timestamp = payload.get("exp")
    if exp_timestamp is None:
        return None
    
    # Convert timestamp to UTC datetime
    return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
