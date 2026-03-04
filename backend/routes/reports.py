"""Reports API routes for lab report upload and management.

This module provides endpoints for report operations including:
- POST /api/reports/upload - Upload lab report files
- GET /api/reports - List user's reports
- GET /api/reports/{report_id} - Get specific report details
- DELETE /api/reports/{report_id} - Delete a report

Requirements: 15.4, 15.5, 15.6, 15.9, 16.1
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging
import asyncio

from models.schemas import Report, PyObjectId
from services.file_storage import FileStorageService, FileStorageError
from services.file_validation import FileValidationError
from services.enhanced_pipeline import process_report_enhanced
from middleware.auth import get_current_user, AuthenticatedUser
from database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


# Response Models

class UploadResponse(BaseModel):
    """Response model for file upload.
    
    Validates: Requirements 15.4
    """
    report_id: str = Field(..., description="Unique report identifier")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Success message")


class ReportSummary(BaseModel):
    """Summary information for a report in list view."""
    id: str = Field(..., description="Report ID")
    file_name: str = Field(..., description="Original filename")
    upload_date: datetime = Field(..., description="Upload timestamp")
    processing_status: str = Field(..., description="Current processing status")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File type")


class ReportsListResponse(BaseModel):
    """Response model for reports list.
    
    Validates: Requirements 15.5
    """
    reports: List[ReportSummary] = Field(..., description="List of user's reports")


class ParameterDetail(BaseModel):
    """Detailed parameter information for report detail view."""
    name: str = Field(..., description="Parameter name")
    value: float = Field(..., description="Parameter value")
    unit: str = Field(..., description="Unit of measurement")
    normal_range: Optional[dict] = Field(None, description="Normal range (min, max)")
    risk_level: str = Field(..., description="Risk level classification")
    explanation: Optional[str] = Field(None, description="AI-generated explanation")
    medical_translation: Optional[str] = Field(None, description="Common language term")
    lifestyle_recommendations: List[str] = Field(default_factory=list, description="Lifestyle suggestions")
    organ_system: Optional[str] = Field(None, description="Organ system")


class ReportDetail(BaseModel):
    """Detailed report information including parameters and explanations.
    
    Validates: Requirements 15.6
    """
    id: str = Field(..., description="Report ID")
    file_name: str = Field(..., description="Original filename")
    upload_date: datetime = Field(..., description="Upload timestamp")
    processing_status: str = Field(..., description="Current processing status")
    parameters: List[ParameterDetail] = Field(default_factory=list, description="Extracted parameters")
    summary: Optional[str] = Field(None, description="Overall summary")
    overall_assessment: Optional[str] = Field(None, description="Overall health assessment")


class DeleteResponse(BaseModel):
    """Response model for report deletion.
    
    Validates: Requirements 15.9
    """
    message: str = Field(..., description="Deletion confirmation message")


# API Endpoints

@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a lab report file",
    description="Upload a PDF or image file (JPEG, PNG) under 10MB for processing.",
)
async def upload_report(
    file: UploadFile = File(..., description="Lab report file (PDF, JPEG, PNG, max 10MB)"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UploadResponse:
    """Upload a lab report file for processing.
    
    This endpoint:
    1. Accepts multipart/form-data file uploads
    2. Validates file type (PDF, JPEG, PNG) and size (max 10MB)
    3. Stores the file using FileStorageService
    4. Creates a report record in the database
    5. Triggers the processing pipeline asynchronously (marks as "processing")
    
    Args:
        file: Uploaded file (multipart/form-data)
        current_user: Authenticated user information (injected)
        db: MongoDB database instance (injected)
    
    Returns:
        UploadResponse with report_id, status, and message
    
    Raises:
        HTTPException 400: If file validation fails (invalid type or size)
        HTTPException 401: If user is not authenticated
        HTTPException 500: If file storage or database operation fails
    
    Validates: Requirements 15.4, 16.1
    """
    try:
        # Get file size
        file.file.seek(0, 2)  # Seek to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        # Initialize file storage service
        storage_service = FileStorageService(db)
        
        # Save file and create report record
        # This validates the file, stores it, and creates the database record
        report = await storage_service.save_file(
            file_content=file.file,
            filename=file.filename,
            file_size=file_size,
            user_id=current_user.user_id,
            content_type=file.content_type
        )
        
        # Trigger processing pipeline asynchronously
        # For now, we'll mark the report as "processing" and trigger OCR
        await db.reports.update_one(
            {"_id": ObjectId(str(report.id))},
            {
                "$set": {
                    "processing_status": "processing",
                    "processing_started_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            "Report uploaded successfully",
            extra={
                "report_id": str(report.id),
                "user_id": current_user.user_id,
                "file_name": file.filename,
                "file_size": file_size,
                "file_type": report.file_type
            }
        )
        
        # Trigger enhanced processing pipeline asynchronously
        # This runs in the background without blocking the response
        # Get user profile for age/gender-specific analysis
        user_doc = await db.users.find_one({"_id": ObjectId(current_user.user_id)})
        user_age = user_doc.get("profile", {}).get("age", 30) if user_doc else 30
        user_gender = user_doc.get("profile", {}).get("gender", "male") if user_doc else "male"
        
        asyncio.create_task(
            process_report_enhanced(
                str(report.id),
                db,
                user_age,
                user_gender
            )
        )
        
        return UploadResponse(
            report_id=str(report.id),
            status="processing",
            message="File uploaded successfully and AI analysis has started"
        )
        
    except FileValidationError as e:
        # File validation failed (invalid type or size)
        logger.warning(
            "File validation failed",
            extra={
                "user_id": current_user.user_id,
                "file_name": file.filename,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileStorageError as e:
        # File storage operation failed
        logger.error(
            "File storage failed",
            extra={
                "user_id": current_user.user_id,
                "file_name": file.filename,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store file. Please try again."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., authentication errors)
        raise
    except Exception as e:
        # Unexpected error
        logger.error(
            "Unexpected error during file upload",
            extra={
                "user_id": current_user.user_id,
                "file_name": file.filename if file else "unknown",
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.get(
    "",
    response_model=ReportsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's reports",
    description="Retrieve a list of all reports uploaded by the authenticated user.",
)
async def get_reports(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> ReportsListResponse:
    """Get list of user's reports.
    
    This endpoint retrieves all reports uploaded by the authenticated user,
    sorted by upload date (most recent first).
    
    Args:
        current_user: Authenticated user information (injected)
        db: MongoDB database instance (injected)
    
    Returns:
        ReportsListResponse with list of report summaries
    
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If database operation fails
    
    Validates: Requirements 15.5
    """
    try:
        # Initialize file storage service
        storage_service = FileStorageService(db)
        
        # Get user's reports
        reports = await storage_service.get_user_reports(current_user.user_id)
        
        # Convert to summary format
        report_summaries = [
            ReportSummary(
                id=str(report.id),
                file_name=report.file_name,
                upload_date=report.upload_date,
                processing_status=report.processing_status,
                file_size=report.file_size,
                file_type=report.file_type
            )
            for report in reports
        ]
        
        logger.info(
            "Reports retrieved successfully",
            extra={
                "user_id": current_user.user_id,
                "report_count": len(report_summaries)
            }
        )
        
        response = ReportsListResponse(reports=report_summaries)
        logger.info(f"Returning response with {len(response.reports)} reports")
        return response
        
    except FileStorageError as e:
        logger.error(
            "Failed to retrieve reports",
            extra={
                "user_id": current_user.user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error retrieving reports",
            extra={
                "user_id": current_user.user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.get(
    "/{report_id}",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
    summary="Get report details",
    description="Retrieve detailed information for a specific report including parameters and explanations.",
)
async def get_report_detail(
    report_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> ReportDetail:
    """Get detailed information for a specific report.
    
    This endpoint:
    1. Verifies the authenticated user owns the report
    2. Returns detailed report information including:
       - Report metadata (file name, upload date, status)
       - Extracted parameters (when available)
       - AI-generated explanations (when available)
       - Overall summary (when available)
    
    Args:
        report_id: ID of the report to retrieve
        current_user: Authenticated user information (injected)
        db: MongoDB database instance (injected)
    
    Returns:
        ReportDetail with complete report information
    
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If report not found or user not authorized
        HTTPException 500: If database operation fails
    
    Validates: Requirements 15.6
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(report_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid report ID format"
            )
        
        # Get report from database (use string user_id)
        report_doc = await db.reports.find_one({
            "_id": ObjectId(report_id),
            "user_id": current_user.user_id
        })
        
        if not report_doc:
            logger.warning(
                "Report not found or unauthorized",
                extra={
                    "report_id": report_id,
                    "user_id": current_user.user_id
                }
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found or you are not authorized to access it"
            )
        
        # Get parameters for this report (if any)
        parameters_cursor = db.parameters.find({
            "report_id": ObjectId(report_id)
        })
        parameters_docs = await parameters_cursor.to_list(length=None)
        
        # Convert parameters to response format
        parameters = []
        for param_doc in parameters_docs:
            # Build normal range dict if available
            normal_range = None
            if param_doc.get("normal_range"):
                nr = param_doc["normal_range"]
                normal_range = {
                    "min": nr.get("min"),
                    "max": nr.get("max")
                }
            
            parameters.append(ParameterDetail(
                name=param_doc.get("parameter_name", ""),
                value=param_doc.get("value", 0.0),
                unit=param_doc.get("unit", ""),
                normal_range=normal_range,
                risk_level=param_doc.get("risk_level", "Unknown"),
                explanation=param_doc.get("explanation"),
                medical_translation=param_doc.get("medical_translation"),
                lifestyle_recommendations=param_doc.get("lifestyle_recommendations", []),
                organ_system=param_doc.get("organ_system")
            ))
        
        logger.info(
            "Report detail retrieved successfully",
            extra={
                "report_id": report_id,
                "user_id": current_user.user_id,
                "parameter_count": len(parameters)
            }
        )
        
        return ReportDetail(
            id=str(report_doc["_id"]),
            file_name=report_doc.get("file_name", ""),
            upload_date=report_doc.get("upload_date", datetime.utcnow()),
            processing_status=report_doc.get("processing_status", "uploaded"),
            parameters=parameters,
            summary=report_doc.get("summary"),  # AI-generated summary from LLM service
            overall_assessment=report_doc.get("overall_assessment")  # Additional assessment if available
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error retrieving report detail",
            extra={
                "report_id": report_id,
                "user_id": current_user.user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.delete(
    "/{report_id}",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a report",
    description="Delete a specific report and its associated file.",
)
async def delete_report(
    report_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> DeleteResponse:
    """Delete a report and its associated file.
    
    This endpoint deletes both the file from storage and the report record
    from the database. Only the report owner can delete their reports.
    
    Args:
        report_id: ID of the report to delete
        current_user: Authenticated user information (injected)
        db: MongoDB database instance (injected)
    
    Returns:
        DeleteResponse with confirmation message
    
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If report not found or user not authorized
        HTTPException 500: If deletion fails
    
    Validates: Requirements 15.9
    """
    try:
        # Initialize file storage service
        storage_service = FileStorageService(db)
        
        # Delete report (includes authorization check)
        deleted = await storage_service.delete_report(report_id, current_user.user_id)
        
        if not deleted:
            logger.warning(
                "Report not found or unauthorized",
                extra={
                    "report_id": report_id,
                    "user_id": current_user.user_id
                }
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found or you are not authorized to delete it"
            )
        
        logger.info(
            "Report deleted successfully",
            extra={
                "report_id": report_id,
                "user_id": current_user.user_id
            }
        )
        
        return DeleteResponse(message="Report deleted successfully")
        
    except HTTPException:
        raise
    except FileStorageError as e:
        logger.error(
            "Failed to delete report",
            extra={
                "report_id": report_id,
                "user_id": current_user.user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report. Please try again."
        )
    except Exception as e:
        logger.error(
            "Unexpected error deleting report",
            extra={
                "report_id": report_id,
                "user_id": current_user.user_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )
