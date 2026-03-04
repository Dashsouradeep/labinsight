"""
NER Service API Routes (Internal/Testing)

This module provides endpoints for testing the NER service directly.
These are primarily for development and testing purposes.

Requirements: 4.1, 4.10
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
import logging

from services.ner_service import get_ner_service, MedicalParameter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ner", tags=["ner"])


# Request/Response Models

class NERRequest(BaseModel):
    """Request model for NER extraction."""
    text: str = Field(..., description="Text to extract parameters from", min_length=1)


class ParameterResponse(BaseModel):
    """Response model for extracted parameter."""
    name: str = Field(..., description="Normalized parameter name")
    value: float = Field(..., description="Parameter value")
    unit: str = Field(..., description="Unit of measurement")
    raw_text: str = Field(..., description="Original text")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")


class NERResponse(BaseModel):
    """Response model for NER extraction."""
    parameters: List[ParameterResponse] = Field(..., description="Extracted parameters")
    count: int = Field(..., description="Number of parameters extracted")


class ModelInfoResponse(BaseModel):
    """Response model for model information."""
    model_name: str
    device: str
    tokenizer_vocab_size: int
    model_loaded: bool
    pipeline_ready: bool


# API Endpoints

@router.post(
    "/extract",
    response_model=NERResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract medical parameters from text",
    description="Use BioClinicalBERT NER to extract medical parameters from lab report text.",
)
async def extract_parameters(request: NERRequest) -> NERResponse:
    """
    Extract medical parameters from text using NER.
    
    This endpoint uses the BioClinicalBERT model to identify and extract
    medical parameters (hemoglobin, WBC, glucose, etc.) from unstructured text.
    
    Args:
        request: NERRequest with text to process
    
    Returns:
        NERResponse with extracted parameters
    
    Raises:
        HTTPException 400: If text is invalid
        HTTPException 500: If NER processing fails
    
    Requirements: 4.1, 4.10
    """
    try:
        # Get NER service instance
        ner_service = get_ner_service()
        
        # Extract parameters
        parameters = ner_service.extract_parameters(request.text)
        
        # Convert to response format
        param_responses = [
            ParameterResponse(
                name=p.name,
                value=p.value,
                unit=p.unit,
                raw_text=p.raw_text,
                confidence=p.confidence
            )
            for p in parameters
        ]
        
        logger.info(f"NER extraction successful: {len(param_responses)} parameters")
        
        return NERResponse(
            parameters=param_responses,
            count=len(param_responses)
        )
        
    except ValueError as e:
        logger.warning(f"Invalid input for NER extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"NER extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract parameters. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error in NER extraction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get NER model information",
    description="Get information about the loaded BioClinicalBERT model.",
)
async def get_model_info() -> ModelInfoResponse:
    """
    Get information about the NER model.
    
    Returns model name, device (GPU/CPU), and status information.
    
    Returns:
        ModelInfoResponse with model details
    
    Raises:
        HTTPException 500: If model is not loaded
    """
    try:
        ner_service = get_ner_service()
        info = ner_service.get_model_info()
        
        return ModelInfoResponse(**info)
        
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model information."
        )
