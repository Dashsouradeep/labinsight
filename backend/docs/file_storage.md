# File Storage Service Documentation

## Overview

The File Storage Service provides functionality for saving uploaded lab report files to the local filesystem and storing their metadata in MongoDB. This service implements Requirements 2.5 and 2.6 from the LabInsight specification.

## Features

- **UUID-based File Naming**: Each uploaded file is saved with a unique UUID-based filename to prevent collisions
- **File Metadata Storage**: File information is stored in the MongoDB `reports` collection
- **User Association**: Files are automatically associated with authenticated users
- **File Validation**: Integrates with file validation utilities to ensure only valid files are stored
- **Authorization**: Users can only access their own files
- **Cleanup on Failure**: If database operations fail, uploaded files are automatically cleaned up

## Architecture

```
┌─────────────────┐
│  Upload Request │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  FileStorageService     │
│  ┌──────────────────┐   │
│  │ 1. Validate File │   │
│  └────────┬─────────┘   │
│           │             │
│  ┌────────▼─────────┐   │
│  │ 2. Generate UUID │   │
│  └────────┬─────────┘   │
│           │             │
│  ┌────────▼─────────┐   │
│  │ 3. Save to Disk  │   │
│  └────────┬─────────┘   │
│           │             │
│  ┌────────▼─────────┐   │
│  │ 4. Store in DB   │   │
│  └────────┬─────────┘   │
│           │             │
│  ┌────────▼─────────┐   │
│  │ 5. Return Report │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

## Usage

### Initialization

```python
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.file_storage import FileStorageService

# Initialize with database connection
database = await get_database()
file_storage = FileStorageService(database)
```

### Saving Files

```python
# Save an uploaded file
report = await file_storage.save_file(
    file_content=file_stream,      # Binary file stream
    filename="lab_report.pdf",      # Original filename
    file_size=1024000,              # File size in bytes
    user_id="507f1f77bcf86cd799439011",  # User ID
    content_type="application/pdf"  # MIME type (optional)
)

# Returns Report object with:
# - id: MongoDB ObjectId
# - user_id: Associated user
# - file_path: Path to saved file
# - file_name: Original filename
# - file_size: Size in bytes
# - file_type: Normalized type (pdf, image/jpeg, image/png)
# - upload_date: Timestamp
# - processing_status: "uploaded"
```

### Retrieving Files

```python
# Get a specific report (with authorization check)
report = await file_storage.get_report(
    report_id="507f1f77bcf86cd799439011",
    user_id="507f1f77bcf86cd799439012"
)

# Get all reports for a user
reports = await file_storage.get_user_reports(
    user_id="507f1f77bcf86cd799439012"
)
# Returns list sorted by upload_date (most recent first)
```

### Deleting Files

```python
# Delete a report and its file (with authorization check)
deleted = await file_storage.delete_report(
    report_id="507f1f77bcf86cd799439011",
    user_id="507f1f77bcf86cd799439012"
)
# Returns True if deleted, False if not found or unauthorized
```

### File Path Operations

```python
# Get filesystem path for a report
file_path = file_storage.get_file_path(report)

# Check if file exists on filesystem
exists = file_storage.file_exists(report)
```

## File Storage Structure

Files are stored in the directory specified by `settings.upload_dir` (default: `./uploads`):

```
uploads/
├── 550e8400-e29b-41d4-a716-446655440000.pdf
├── 6ba7b810-9dad-11d1-80b4-00c04fd430c8.png
└── 7c9e6679-7425-40de-944b-e07fc1f90ae7.jpg
```

Each file is named using its UUID with the original file extension preserved.

## Database Schema

Files are stored in the `reports` collection with the following structure:

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  user_id: ObjectId("507f1f77bcf86cd799439012"),
  file_path: "./uploads/550e8400-e29b-41d4-a716-446655440000.pdf",
  file_name: "lab_report_2024.pdf",
  file_size: 1024000,
  file_type: "pdf",
  upload_date: ISODate("2024-01-15T10:30:00Z"),
  processing_status: "uploaded",
  processing_started_at: null,
  processing_completed_at: null,
  ocr_text: null,
  error_message: null
}
```

## Error Handling

### FileStorageError

Raised when file storage operations fail:

```python
try:
    report = await file_storage.save_file(...)
except FileStorageError as e:
    # Handle storage error
    print(f"Failed to save file: {e}")
```

### FileValidationError

Raised when file validation fails (from file_validation module):

```python
from services.file_validation import FileValidationError

try:
    report = await file_storage.save_file(...)
except FileValidationError as e:
    # Handle validation error (invalid type or size)
    print(f"Invalid file: {e}")
```

### Automatic Cleanup

If database operations fail after a file is saved to disk, the file is automatically deleted to prevent orphaned files:

```python
# If this fails:
result = await self.database.reports.insert_one(...)

# The saved file is automatically cleaned up:
if file_path.exists():
    file_path.unlink()
```

## Security Considerations

### Authorization

All retrieval and deletion operations include authorization checks:

```python
# Users can only access their own reports
report = await file_storage.get_report(
    report_id=report_id,
    user_id=current_user_id  # Must match report owner
)
# Returns None if user doesn't own the report
```

### File Validation

All files are validated before storage:
- File type must be PDF, JPEG, or PNG
- File size must not exceed 10MB
- Validation is performed by the `file_validation` module

### UUID-based Naming

Files are stored with UUID-based names to:
- Prevent filename collisions
- Avoid path traversal attacks
- Obscure original filenames from unauthorized users

## Configuration

File storage behavior is configured via environment variables:

```env
# Upload directory (default: ./uploads)
UPLOAD_DIR=./uploads

# Maximum file size in MB (default: 10)
MAX_FILE_SIZE_MB=10
```

## Integration with Processing Pipeline

The file storage service is the first step in the report processing pipeline:

1. **Upload**: File is saved to filesystem and metadata stored in database
2. **OCR**: Text is extracted from the saved file
3. **NER**: Medical parameters are extracted from OCR text
4. **Analysis**: Parameters are analyzed and explanations generated
5. **Trends**: Multi-report trends are calculated

The `processing_status` field tracks the report's progress through the pipeline:
- `uploaded`: File saved, awaiting processing
- `processing`: Currently being processed
- `completed`: Processing finished successfully
- `failed`: Processing encountered an error

## Testing

The file storage service includes comprehensive unit tests:

```bash
# Run file storage tests
pytest tests/test_file_storage.py -v

# Run with coverage
pytest tests/test_file_storage.py --cov=services.file_storage
```

Test coverage includes:
- Saving PDF and image files
- UUID-based filename generation
- User association
- File validation (size and type)
- Report retrieval with authorization
- Report deletion with authorization
- File existence checking
- Cleanup on database errors

## Requirements Validation

This service validates the following requirements:

- **Requirement 2.5**: Generate unique report identifier (UUID)
- **Requirement 2.6**: Associate file with authenticated user's account

## Related Documentation

- [File Validation](./file_validation.md) - File type and size validation
- [MongoDB Connection Manager](./mongodb_connection_manager.md) - Database connection handling
- [Database Indexes](./database_indexes.md) - Database performance optimization

## Future Enhancements

Potential improvements for production deployment:

1. **Cloud Storage**: Replace local filesystem with S3-compatible storage
2. **File Compression**: Compress files to save storage space
3. **Virus Scanning**: Integrate antivirus scanning before storage
4. **Thumbnails**: Generate thumbnails for image files
5. **Encryption**: Encrypt files at rest for enhanced security
6. **Backup**: Implement automated backup of uploaded files
7. **Retention Policy**: Implement automatic deletion of old files
