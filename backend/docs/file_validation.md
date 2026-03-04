# File Validation Utilities

## Overview

The file validation module provides utilities for validating uploaded lab report files before processing. It ensures that only supported file types (PDF, JPEG, PNG) under the size limit (10MB) are accepted for upload.

## Requirements

Validates Requirements 2.1-2.4:
- 2.1: Accept PDF files under 10MB
- 2.2: Accept image files (JPEG, PNG) under 10MB
- 2.3: Reject files exceeding 10MB with size limit error
- 2.4: Reject unsupported file types with format error

## Module: `services.file_validation`

### Constants

- `MAX_FILE_SIZE_BYTES`: Maximum allowed file size (10MB = 10,485,760 bytes)
- `ALLOWED_FILE_TYPES`: Dictionary mapping MIME types to normalized file types
- `ALLOWED_EXTENSIONS`: Set of allowed file extensions (.pdf, .jpg, .jpeg, .png)

### Functions

#### `validate_file_type(filename: str, content_type: Optional[str] = None) -> Literal["pdf", "image/jpeg", "image/png"]`

Validates that the file type is supported (PDF, JPEG, PNG).

**Parameters:**
- `filename`: Name of the uploaded file
- `content_type`: MIME type of the file (optional)

**Returns:**
- Normalized file type string: "pdf", "image/jpeg", or "image/png"

**Raises:**
- `FileValidationError`: If file type is not supported

**Example:**
```python
from services import validate_file_type, FileValidationError

try:
    file_type = validate_file_type("report.pdf", "application/pdf")
    print(f"Valid file type: {file_type}")
except FileValidationError as e:
    print(f"Invalid file: {e}")
```

#### `validate_file_size(file_size: int) -> None`

Validates that the file size is within the allowed limit (10MB).

**Parameters:**
- `file_size`: Size of the file in bytes

**Raises:**
- `FileValidationError`: If file size exceeds 10MB or is <= 0

**Example:**
```python
from services import validate_file_size, FileValidationError

try:
    validate_file_size(5 * 1024 * 1024)  # 5MB - OK
    print("File size is valid")
except FileValidationError as e:
    print(f"Invalid file size: {e}")
```

#### `generate_report_id() -> str`

Generates a unique report identifier using UUID4.

**Returns:**
- Unique report ID as a string (UUID4 format)

**Example:**
```python
from services import generate_report_id

report_id = generate_report_id()
print(f"Generated report ID: {report_id}")
# Output: Generated report ID: 550e8400-e29b-41d4-a716-446655440000
```

#### `validate_file(filename: str, file_size: int, content_type: Optional[str] = None) -> Literal["pdf", "image/jpeg", "image/png"]`

Validates a file for upload (combines type and size validation).

**Parameters:**
- `filename`: Name of the uploaded file
- `file_size`: Size of the file in bytes
- `content_type`: MIME type of the file (optional)

**Returns:**
- Normalized file type string: "pdf", "image/jpeg", or "image/png"

**Raises:**
- `FileValidationError`: If validation fails (size or type)

**Example:**
```python
from services import validate_file, FileValidationError

try:
    file_type = validate_file("scan.jpg", 3 * 1024 * 1024, "image/jpeg")
    print(f"File is valid: {file_type}")
except FileValidationError as e:
    print(f"Validation failed: {e}")
```

### Exception: `FileValidationError`

Custom exception raised when file validation fails. Inherits from `Exception`.

**Usage:**
```python
from services import FileValidationError

try:
    # validation code
    pass
except FileValidationError as e:
    # Handle validation error
    error_message = str(e)
```

## Usage in Upload Endpoint

The file validation utilities are designed to be used in the file upload endpoint:

```python
from fastapi import UploadFile, HTTPException
from services import validate_file, generate_report_id, FileValidationError

async def upload_report(file: UploadFile):
    try:
        # Read file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        # Validate file
        file_type = validate_file(
            filename=file.filename,
            file_size=file_size,
            content_type=file.content_type
        )
        
        # Generate unique report ID
        report_id = generate_report_id()
        
        # Process file...
        
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Supported File Types

### PDF Files
- Extensions: `.pdf`
- MIME type: `application/pdf`
- Use case: Lab reports in PDF format

### JPEG Images
- Extensions: `.jpg`, `.jpeg`
- MIME type: `image/jpeg`
- Use case: Scanned lab reports as JPEG images

### PNG Images
- Extensions: `.png`
- MIME type: `image/png`
- Use case: Scanned lab reports as PNG images

## File Size Limits

- **Maximum size**: 10MB (10,485,760 bytes)
- **Minimum size**: Greater than 0 bytes
- Files exceeding the limit are rejected with a descriptive error message including the actual file size

## Error Messages

The module provides user-friendly error messages:

### Size Errors
```
File size exceeds the maximum limit of 10MB. File size: 15.50MB
```

### Type Errors (Extension)
```
Unsupported file type. Only PDF, JPEG, and PNG files are allowed. Got extension: .docx
```

### Type Errors (MIME Type)
```
Unsupported file type. Only PDF, JPEG, and PNG files are allowed. Got content type: text/plain
```

## Testing

Comprehensive unit tests are available in `tests/test_file_validation.py`:

```bash
# Run all file validation tests
pytest tests/test_file_validation.py -v

# Run specific test class
pytest tests/test_file_validation.py::TestFileTypeValidation -v

# Run with coverage
pytest tests/test_file_validation.py --cov=services.file_validation
```

## Implementation Notes

1. **Extension Checking**: File extensions are checked case-insensitively (`.PDF`, `.pdf`, `.Pdf` all work)

2. **Content Type Priority**: When both filename and content_type are provided, content_type is validated first for security

3. **UUID Generation**: Uses UUID4 for cryptographically strong random IDs

4. **Performance**: File size is validated before file type for faster rejection of oversized files

5. **Security**: Both extension and MIME type can be validated to prevent file type spoofing
