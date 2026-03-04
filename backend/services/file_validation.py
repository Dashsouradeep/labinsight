"""File validation utilities for lab report uploads.

This module provides utilities for validating uploaded files, including:
- File type validation (PDF, JPEG, PNG)
- File size validation (max 10MB)
- Unique report ID generation (UUID)

Requirements: 2.1-2.4
"""

import uuid
from typing import Literal, Optional
from pathlib import Path


# Constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "image/jpeg",
    "image/png": "image/png"
}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class FileValidationError(Exception):
    """Exception raised when file validation fails."""
    pass


def validate_file_type(filename: str, content_type: Optional[str] = None) -> Literal["pdf", "image/jpeg", "image/png"]:
    """Validate that the file type is supported (PDF, JPEG, PNG).
    
    Args:
        filename: Name of the uploaded file
        content_type: MIME type of the file (optional)
        
    Returns:
        Normalized file type string
        
    Raises:
        FileValidationError: If file type is not supported
        
    Validates: Requirements 2.2, 2.4
    """
    # If content_type is provided, validate it first
    if content_type:
        if content_type not in ALLOWED_FILE_TYPES:
            raise FileValidationError(
                f"Unsupported file type. Only PDF, JPEG, and PNG files are allowed. "
                f"Got content type: {content_type}"
            )
        return ALLOWED_FILE_TYPES[content_type]
    
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file type. Only PDF, JPEG, and PNG files are allowed. "
            f"Got extension: {file_ext}"
        )
    
    # Map extension to file type
    if file_ext == ".pdf":
        return "pdf"
    elif file_ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    elif file_ext == ".png":
        return "image/png"
    
    # This should never be reached due to the extension check above
    raise FileValidationError(f"Unsupported file extension: {file_ext}")


def validate_file_size(file_size: int) -> None:
    """Validate that the file size is within the allowed limit (10MB).
    
    Args:
        file_size: Size of the file in bytes
        
    Raises:
        FileValidationError: If file size exceeds 10MB
        
    Validates: Requirements 2.1, 2.3
    """
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        raise FileValidationError(
            f"File size exceeds the maximum limit of 10MB. "
            f"File size: {size_mb:.2f}MB"
        )
    
    if file_size <= 0:
        raise FileValidationError("File size must be greater than 0 bytes")


def generate_report_id() -> str:
    """Generate a unique report identifier using UUID4.
    
    Returns:
        Unique report ID as a string
        
    Validates: Requirements 2.5
    """
    return str(uuid.uuid4())


def validate_file(filename: str, file_size: int, content_type: Optional[str] = None) -> Literal["pdf", "image/jpeg", "image/png"]:
    """Validate a file for upload (combines type and size validation).
    
    Args:
        filename: Name of the uploaded file
        file_size: Size of the file in bytes
        content_type: MIME type of the file (optional)
        
    Returns:
        Normalized file type string
        
    Raises:
        FileValidationError: If validation fails
        
    Validates: Requirements 2.1-2.4
    """
    # Validate file size first (faster check)
    validate_file_size(file_size)
    
    # Validate file type
    file_type = validate_file_type(filename, content_type)
    
    return file_type
