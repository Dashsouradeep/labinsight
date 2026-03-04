"""File storage service for lab report uploads.

This module provides utilities for saving uploaded files to the local filesystem
and storing file metadata in the MongoDB reports collection.

Requirements: 2.5, 2.6
"""

import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from config import settings
from models.schemas import Report, PyObjectId
from services.file_validation import generate_report_id, validate_file


class FileStorageError(Exception):
    """Exception raised when file storage operations fail."""
    pass


class FileStorageService:
    """Service for handling file storage operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """Initialize file storage service.
        
        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.upload_dir = Path(settings.upload_dir)
        
        # Ensure upload directory exists
        self._ensure_upload_directory()
    
    def _ensure_upload_directory(self) -> None:
        """Create upload directory if it doesn't exist."""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileStorageError(f"Failed to create upload directory: {str(e)}")
    
    async def save_file(
        self,
        file_content: BinaryIO,
        filename: str,
        file_size: int,
        user_id: str,
        content_type: Optional[str] = None
    ) -> Report:
        """Save uploaded file to filesystem and create report record in database.
        
        This function:
        1. Validates the file (type and size)
        2. Generates a unique UUID-based filename
        3. Saves the file to local filesystem
        4. Creates a report record in MongoDB with file metadata
        5. Associates the file with the authenticated user
        
        Args:
            file_content: Binary file content stream
            filename: Original filename
            file_size: Size of file in bytes
            user_id: ID of the user uploading the file
            content_type: MIME type of the file (optional)
            
        Returns:
            Report object with file metadata
            
        Raises:
            FileStorageError: If file storage or database operation fails
            FileValidationError: If file validation fails
            
        Validates: Requirements 2.5, 2.6
        """
        # Validate file type and size
        file_type = validate_file(filename, file_size, content_type)
        
        # Generate unique report ID (UUID)
        report_id = generate_report_id()
        
        # Determine file extension from original filename
        file_ext = Path(filename).suffix.lower()
        
        # Create UUID-based filename
        uuid_filename = f"{report_id}{file_ext}"
        file_path = self.upload_dir / uuid_filename
        
        try:
            # Save file to filesystem
            with open(file_path, 'wb') as f:
                # Copy file content to destination
                shutil.copyfileobj(file_content, f)
            
            # Create report record in database
            report = Report(
                id=PyObjectId(ObjectId()),
                user_id=PyObjectId(user_id),
                file_path=str(file_path),
                file_name=filename,
                file_size=file_size,
                file_type=file_type,
                upload_date=datetime.utcnow(),
                processing_status="uploaded"
            )
            
            # Insert report into MongoDB
            result = await self.database.reports.insert_one(
                report.model_dump(by_alias=True, exclude={'id'})
            )
            
            # Update report with generated ID
            report.id = PyObjectId(result.inserted_id)
            
            return report
            
        except Exception as e:
            # Clean up file if database operation fails
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as cleanup_error:
                    # Log cleanup error but raise original error
                    pass
            
            raise FileStorageError(f"Failed to save file: {str(e)}")
    
    async def get_report(self, report_id: str, user_id: str) -> Optional[Report]:
        """Retrieve report metadata from database.
        
        Args:
            report_id: ID of the report to retrieve
            user_id: ID of the user (for authorization check)
            
        Returns:
            Report object if found and user is authorized, None otherwise
        """
        try:
            report_data = await self.database.reports.find_one({
                "_id": ObjectId(report_id),
                "user_id": user_id  # Use string user_id
            })
            
            if report_data:
                return Report(**report_data)
            return None
            
        except Exception as e:
            raise FileStorageError(f"Failed to retrieve report: {str(e)}")
    
    async def get_user_reports(self, user_id: str) -> list[Report]:
        """Retrieve all reports for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Report objects
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Query with string user_id (reports are stored with string user_id)
            query = {"user_id": user_id}
            logger.info(f"Querying reports with: {query}")
            
            cursor = self.database.reports.find(query).sort("upload_date", -1)  # Most recent first
            
            reports = []
            async for report_data in cursor:
                logger.info(f"Found report: {report_data.get('_id')}")
                reports.append(Report(**report_data))
            
            logger.info(f"Total reports found: {len(reports)}")
            return reports
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_user_reports: {str(e)}", exc_info=True)
            raise FileStorageError(f"Failed to retrieve user reports: {str(e)}")
    
    async def delete_report(self, report_id: str, user_id: str) -> bool:
        """Delete report file and database record.
        
        Args:
            report_id: ID of the report to delete
            user_id: ID of the user (for authorization check)
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            FileStorageError: If deletion fails
        """
        try:
            # Get report to find file path
            report = await self.get_report(report_id, user_id)
            
            if not report:
                return False
            
            # Delete file from filesystem
            file_path = Path(report.file_path)
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    # Log but continue with database deletion
                    pass
            
            # Delete report from database (use string user_id)
            result = await self.database.reports.delete_one({
                "_id": ObjectId(report_id),
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise FileStorageError(f"Failed to delete report: {str(e)}")
    
    def get_file_path(self, report: Report) -> Path:
        """Get the filesystem path for a report's file.
        
        Args:
            report: Report object
            
        Returns:
            Path object pointing to the file
        """
        return Path(report.file_path)
    
    def file_exists(self, report: Report) -> bool:
        """Check if a report's file exists on filesystem.
        
        Args:
            report: Report object
            
        Returns:
            True if file exists, False otherwise
        """
        return self.get_file_path(report).exists()
