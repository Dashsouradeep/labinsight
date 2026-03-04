"""Pydantic models for MongoDB collections.

This module defines all data models for the LabInsight platform, corresponding
to MongoDB collections as specified in Requirements 13.2-13.6.
"""
from datetime import datetime
from typing import List, Optional, Literal, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class UserProfile(BaseModel):
    """User profile information with age and gender."""
    age: int = Field(..., ge=0, le=150, description="User's age in years")
    gender: Literal["male", "female", "other"] = Field(..., description="User's gender")
    name: Optional[str] = Field(None, description="User's name (optional)")


class User(BaseModel):
    """User model for authentication and profile data.
    
    Corresponds to 'users' collection in MongoDB.
    Requirements: 13.2
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "email": "patient@example.com",
                "password_hash": "$2b$12$...",
                "profile": {
                    "age": 35,
                    "gender": "female",
                    "name": "Jane Doe"
                },
                "terms_accepted": True
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr = Field(..., description="User's email address (unique)")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    profile: UserProfile
    terms_accepted: bool = Field(default=False, description="Whether user accepted terms of service")
    terms_accepted_at: Optional[datetime] = Field(None, description="When terms were accepted")


class Report(BaseModel):
    """Report model for uploaded lab reports with processing status.
    
    Corresponds to 'reports' collection in MongoDB.
    Requirements: 13.3
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "file_path": "/uploads/abc123.pdf",
                "file_name": "lab_report_2024.pdf",
                "file_size": 524288,
                "file_type": "pdf",
                "processing_status": "completed"
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to user who uploaded the report")
    file_path: str = Field(..., description="Path to stored file")
    file_name: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    file_type: Literal["pdf", "image/jpeg", "image/png"] = Field(..., description="MIME type of file")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processing_status: Literal["uploaded", "processing", "completed", "failed"] = Field(
        default="uploaded",
        description="Current processing status"
    )
    processing_started_at: Optional[datetime] = Field(None, description="When processing started")
    processing_completed_at: Optional[datetime] = Field(None, description="When processing completed")
    ocr_text: Optional[str] = Field(None, description="Extracted text from OCR")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")


class NormalRange(BaseModel):
    """Normal range for a medical parameter."""
    min_value: float = Field(..., description="Minimum normal value")
    max_value: float = Field(..., description="Maximum normal value")
    unit: str = Field(..., description="Unit of measurement")
    age_range: tuple[int, int] = Field(..., description="Age range (min, max)")
    gender: Literal["male", "female", "general"] = Field(..., description="Gender specificity")


class Parameter(BaseModel):
    """Medical parameter extracted from lab report with risk classification.
    
    Corresponds to 'parameters' collection in MongoDB.
    Requirements: 13.4
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "report_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "parameter_name": "hemoglobin",
                "value": 14.5,
                "unit": "g/dL",
                "raw_text": "Hemoglobin: 14.5 g/dL",
                "confidence": 0.95,
                "normal_range": {
                    "min_value": 12.0,
                    "max_value": 15.5,
                    "unit": "g/dL",
                    "age_range": [18, 65],
                    "gender": "female"
                },
                "risk_level": "Normal",
                "organ_system": "blood"
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    report_id: PyObjectId = Field(..., description="Reference to parent report")
    user_id: PyObjectId = Field(..., description="Reference to user (for indexing)")
    parameter_name: str = Field(..., description="Normalized parameter name")
    value: float = Field(..., description="Numeric value of the parameter")
    unit: str = Field(..., description="Unit of measurement")
    raw_text: str = Field(..., description="Original text from OCR")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")
    normal_range: Optional[NormalRange] = Field(None, description="Age/gender-specific normal range")
    risk_level: Literal["Normal", "Mild Abnormal", "Critical", "Unknown"] = Field(
        ...,
        description="Risk classification"
    )
    organ_system: Optional[str] = Field(None, description="Organ system (Blood, Liver, Kidney, etc.)")
    medical_translation: Optional[str] = Field(None, description="Common language term")
    explanation: Optional[str] = Field(None, description="AI-generated explanation")
    lifestyle_recommendations: List[str] = Field(default_factory=list, description="Lifestyle suggestions")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class TrendDataPoint(BaseModel):
    """Single data point in a trend history."""
    report_id: PyObjectId = Field(..., description="Reference to report")
    date: datetime = Field(..., description="Date of the report")
    value: float = Field(..., description="Parameter value")
    unit: str = Field(..., description="Unit of measurement")
    risk_level: Literal["Normal", "Mild Abnormal", "Critical", "Unknown"] = Field(
        ...,
        description="Risk level at this point"
    )


class TrendHistory(BaseModel):
    """Trend history for tracking parameter changes over time.
    
    Corresponds to 'trend_history' collection in MongoDB.
    Requirements: 13.5
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "parameter_name": "hemoglobin",
                "data_points": [
                    {
                        "report_id": "507f1f77bcf86cd799439012",
                        "date": "2024-01-01T00:00:00Z",
                        "value": 13.0,
                        "unit": "g/dL",
                        "risk_level": "Mild Abnormal"
                    },
                    {
                        "report_id": "507f1f77bcf86cd799439013",
                        "date": "2024-02-01T00:00:00Z",
                        "value": 14.5,
                        "unit": "g/dL",
                        "risk_level": "Normal"
                    }
                ],
                "trend_direction": "Improving",
                "change_percent": 11.5,
                "summary": "Your hemoglobin improved over the last 2 reports"
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to user")
    parameter_name: str = Field(..., description="Parameter being tracked")
    data_points: List[TrendDataPoint] = Field(..., description="Historical data points")
    trend_direction: Literal["Improving", "Worsening", "Stable", "Insufficient Data"] = Field(
        ...,
        description="Overall trend direction"
    )
    change_percent: float = Field(..., description="Percentage change from previous to latest")
    summary: str = Field(..., description="Plain-language trend summary")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('data_points')
    @classmethod
    def validate_data_points(cls, v):
        """Ensure at least one data point exists."""
        if len(v) < 1:
            raise ValueError("At least one data point is required")
        return v


class AgeGenderRange(BaseModel):
    """Age and gender-specific range for a medical parameter."""
    age_min: int = Field(..., ge=0, description="Minimum age for this range")
    age_max: int = Field(..., le=150, description="Maximum age for this range")
    gender: Literal["male", "female", "general"] = Field(..., description="Gender specificity")
    min_value: float = Field(..., description="Minimum normal value")
    max_value: float = Field(..., description="Maximum normal value")
    unit: str = Field(..., description="Unit of measurement")


class MedicalRange(BaseModel):
    """Medical reference ranges for parameters with age/gender specificity.
    
    Corresponds to 'medical_ranges' collection in MongoDB.
    Requirements: 13.6
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "parameter": "hemoglobin",
                "ranges": [
                    {
                        "age_min": 18,
                        "age_max": 65,
                        "gender": "male",
                        "min_value": 13.5,
                        "max_value": 17.5,
                        "unit": "g/dL"
                    },
                    {
                        "age_min": 18,
                        "age_max": 65,
                        "gender": "female",
                        "min_value": 12.0,
                        "max_value": 15.5,
                        "unit": "g/dL"
                    }
                ],
                "organ_system": "blood",
                "critical_threshold_percent": 20.0,
                "source": "WHO Clinical Guidelines"
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    parameter: str = Field(..., description="Parameter name (indexed)")
    ranges: List[AgeGenderRange] = Field(..., description="List of age/gender-specific ranges")
    organ_system: str = Field(..., description="Organ system (Blood, Liver, Kidney, Thyroid, etc.)")
    critical_threshold_percent: float = Field(
        default=20.0,
        ge=0.0,
        le=100.0,
        description="Deviation percentage for critical classification"
    )
    source: str = Field(..., description="Reference source for these ranges")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('ranges')
    @classmethod
    def validate_ranges(cls, v):
        """Ensure at least one range exists."""
        if len(v) < 1:
            raise ValueError("At least one range is required")
        return v


class MedicalTranslation(BaseModel):
    """Medical term translations to common language.
    
    Corresponds to 'medical_translations' collection in MongoDB.
    Requirements: 13.6
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "medical_term": "Hyperlipidemia",
                "common_term": "High cholesterol",
                "simple_explanation": "Your body has too much fat in the blood",
                "category": "condition"
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    medical_term: str = Field(..., description="Medical terminology (indexed)")
    common_term: str = Field(..., description="Common language equivalent")
    simple_explanation: str = Field(..., description="Simple explanation for patients")
    category: str = Field(..., description="Category (condition, test, organ, etc.)")


class LifestyleRecommendation(BaseModel):
    """Lifestyle recommendations for abnormal parameters.
    
    Used for storing recommendation templates in the database.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "parameter": "cholesterol",
                "risk_level": "mild_abnormal",
                "recommendations": [
                    "Reduce saturated fat intake",
                    "Exercise 30 minutes daily",
                    "Increase fiber-rich foods"
                ]
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    parameter: str = Field(..., description="Parameter name")
    risk_level: Literal["mild_abnormal", "critical"] = Field(..., description="Risk level")
    recommendations: List[str] = Field(..., description="List of lifestyle suggestions")
