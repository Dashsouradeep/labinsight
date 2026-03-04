# Authentication Middleware Documentation

## Overview

The authentication middleware provides JWT token validation, token blacklist checking, and user information extraction for protected routes in the LabInsight platform.

**Requirements:** 12.3

## Components

### 1. `get_current_user` Dependency

The main authentication dependency function that validates JWT tokens and extracts user information.

**Features:**
- Validates JWT token from Authorization header
- Checks token signature and expiration
- Verifies token is not blacklisted in Redis
- Extracts user ID and email from token payload
- Returns `AuthenticatedUser` object

**Error Handling:**
- Returns HTTP 401 for missing, invalid, expired, or blacklisted tokens
- Fails closed (denies access) if Redis check fails for security

### 2. `AuthenticatedUser` Class

Container class for authenticated user information.

**Attributes:**
- `user_id` (str): Unique identifier for the user
- `email` (str): User's email address

## Usage Examples

### Basic Protected Route

```python
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user, AuthenticatedUser

router = APIRouter()

@router.get("/api/protected-resource")
async def get_protected_resource(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Protected route that requires authentication."""
    return {
        "message": "Access granted",
        "user_id": current_user.user_id,
        "email": current_user.email
    }
```

### Using the Convenience Alias

```python
from fastapi import APIRouter
from middleware.auth import CurrentUser, AuthenticatedUser

router = APIRouter()

@router.get("/api/user/profile")
async def get_user_profile(current_user: AuthenticatedUser = CurrentUser):
    """Get current user's profile."""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email
    }
```

### Accessing User Information in Route Logic

```python
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user, AuthenticatedUser
from database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("/api/reports")
async def get_user_reports(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all reports for the authenticated user."""
    # Use current_user.user_id to filter reports
    reports = await db.reports.find(
        {"user_id": current_user.user_id}
    ).to_list(length=100)
    
    return {"reports": reports}
```

### Multiple Dependencies

```python
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user, AuthenticatedUser
from database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.post("/api/reports/upload")
async def upload_report(
    file: UploadFile,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload a new report for the authenticated user."""
    # Associate report with current user
    report_data = {
        "user_id": current_user.user_id,
        "file_name": file.filename,
        "uploaded_by": current_user.email,
        # ... other fields
    }
    
    result = await db.reports.insert_one(report_data)
    return {"report_id": str(result.inserted_id)}
```

## Authentication Flow

1. **Client Request**: Client sends request with `Authorization: Bearer <token>` header
2. **Header Validation**: Middleware checks header format and extracts token
3. **Token Validation**: Validates JWT signature and expiration using `validate_token()`
4. **Blacklist Check**: Queries Redis to check if token is blacklisted
5. **User Extraction**: Extracts user_id and email from token payload
6. **Access Granted**: Returns `AuthenticatedUser` object to route handler

## Error Responses

### Missing Authorization Header
```json
{
  "detail": "Authorization header is required"
}
```
**Status Code:** 401 Unauthorized

### Invalid Header Format
```json
{
  "detail": "Invalid authorization header format. Expected: Bearer <token>"
}
```
**Status Code:** 401 Unauthorized

### Invalid or Expired Token
```json
{
  "detail": "Invalid or expired token"
}
```
**Status Code:** 401 Unauthorized

### Blacklisted Token
```json
{
  "detail": "Token has been invalidated. Please log in again."
}
```
**Status Code:** 401 Unauthorized

### Redis Error (Fail Closed)
```json
{
  "detail": "Unable to validate token. Please try again."
}
```
**Status Code:** 401 Unauthorized

## Security Features

### 1. Token Blacklist
- Tokens are checked against Redis blacklist on every request
- Blacklisted tokens are rejected even if signature is valid
- Implements logout functionality (Requirement 1.7)

### 2. Fail Closed
- If Redis check fails, access is denied for security
- Prevents authentication bypass if Redis is unavailable

### 3. Token Expiration
- Tokens expire after 24 hours (Requirement 1.6)
- Expired tokens are automatically rejected

### 4. Signature Validation
- JWT signature is validated using SECRET_KEY from settings
- Prevents token tampering

## Testing

The middleware includes comprehensive unit tests covering:
- ✅ Successful authentication with valid token
- ✅ Missing Authorization header
- ✅ Invalid header format
- ✅ Empty token
- ✅ Invalid token signature
- ✅ Expired token
- ✅ Blacklisted token
- ✅ Redis error handling (fail closed)
- ✅ User information extraction
- ✅ Multiple valid tokens for different users
- ✅ Edge cases (whitespace, case sensitivity, malformed JWT)

Run tests with:
```bash
pytest tests/test_auth_middleware.py -v
```

## Configuration

The middleware uses settings from `config.py`:

```python
# JWT Configuration
jwt_secret_key: str  # Secret key for JWT signing (required)
jwt_algorithm: str = "HS256"  # JWT algorithm
jwt_expiration_hours: int = 24  # Token expiration time
```

**Important:** Set `jwt_secret_key` in your `.env` file:
```
JWT_SECRET_KEY=your-secure-secret-key-here
```

## Integration with Existing Routes

To protect existing routes, simply add the dependency:

```python
# Before (unprotected)
@router.get("/api/reports")
async def get_reports():
    # Anyone can access
    pass

# After (protected)
@router.get("/api/reports")
async def get_reports(current_user: AuthenticatedUser = Depends(get_current_user)):
    # Only authenticated users can access
    # Use current_user.user_id to filter data
    pass
```

## Logging

The middleware logs authentication events:
- **DEBUG**: Successful authentication
- **WARNING**: Invalid tokens, missing headers, blacklisted tokens
- **ERROR**: Redis errors, missing payload fields

All logs include contextual information (user_id, email) when available.

## Related Components

- **auth_service.py**: JWT token generation and validation
- **redis_client.py**: Token blacklist management
- **routes/auth.py**: Login/logout endpoints that issue and blacklist tokens

## Requirements Validation

This middleware validates **Requirement 12.3**:
> WHEN a service receives a request, THE System SHALL validate authentication tokens

The implementation:
1. ✅ Validates JWT token on protected routes
2. ✅ Checks token blacklist in Redis
3. ✅ Extracts user ID from token
4. ✅ Returns appropriate HTTP 401 errors for invalid tokens
5. ✅ Provides user information to route handlers
