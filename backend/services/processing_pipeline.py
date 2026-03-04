"""
Complete Processing Pipeline - MVP Version
Orchestrates OCR → Parameter Extraction → Risk Classification → Storage
"""

import logging
from typing import Optional
from datetime import datetime
from bson import ObjectId

from services.ocr_service_tesseract import get_ocr_service
from services.simple_parameter_extractor import (
    extract_parameters,
    classify_risk,
    get_normal_range,
    generate_simple_explanation
)

logger = logging.getLogger(__name__)


async def process_report_complete(report_id: str, database, user_gender: str = "male"):
    """
    Complete end-to-end processing pipeline for a lab report.
    
    Steps:
    1. Run OCR to extract text
    2. Extract parameters using regex
    3. Classify risk levels
    4. Generate explanations
    5. Store everything in database
    
    Args:
        report_id: Report ID to process
        database: Database connection
        user_gender: User's gender for range selection
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Starting complete processing for report {report_id}")
        
        # Validate report ID
        if not ObjectId.is_valid(report_id):
            logger.error(f"Invalid report ID: {report_id}")
            return False
        
        # Get report from database
        report = await database.reports.find_one({"_id": ObjectId(report_id)})
        if not report:
            logger.error(f"Report not found: {report_id}")
            return False
        
        # Update status to processing
        await database.reports.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": {"processing_status": "processing", "processing_started_at": datetime.utcnow()}}
        )
        
        # STEP 1: OCR - Extract text from file
        logger.info("Step 1: Running OCR...")
        file_path = report.get("file_path")
        file_type = report.get("file_type", "")
        
        if not file_path:
            raise ValueError("No file path found")
        
        ocr_service = get_ocr_service()
        
        if file_type == "pdf":
            ocr_results = ocr_service.extract_from_pdf(file_path)
            extracted_text = "\n\n".join([f"Page {r.page_number}:\n{r.text}" for r in ocr_results])
        else:
            ocr_result = ocr_service.extract_from_image(file_path)
            extracted_text = ocr_result.text
        
        if not extracted_text or not extracted_text.strip():
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "No text could be extracted from the image.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
            return False
        
        # Store OCR text
        await database.reports.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": {"ocr_text": extracted_text}}
        )
        logger.info(f"OCR complete: {len(extracted_text)} characters extracted")
        
        # STEP 2: Extract parameters
        logger.info("Step 2: Extracting parameters...")
        parameters = extract_parameters(extracted_text)
        
        if not parameters:
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "completed",
                        "summary": "No medical parameters could be detected in this report. Please ensure the image is clear and contains lab test results.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
            return True
        
        logger.info(f"Extracted {len(parameters)} parameters")
        
        # STEP 3 & 4: Classify risk and generate explanations
        logger.info("Step 3-4: Classifying risk and generating explanations...")
        parameter_docs = []
        
        for param in parameters:
            # Classify risk
            risk_level = classify_risk(param.name, param.value, user_gender)
            
            # Get normal range
            normal_range = get_normal_range(param.name, user_gender)
            
            # Generate explanation
            explanation = generate_simple_explanation(param.name, param.value, risk_level, user_gender)
            
            # Create parameter document
            param_doc = {
                "report_id": ObjectId(report_id),
                "user_id": report.get("user_id"),
                "parameter_name": param.name,
                "value": param.value,
                "unit": param.unit,
                "raw_text": param.raw_text,
                "confidence": param.confidence,
                "normal_range": {
                    "min": normal_range["min"] if normal_range else 0,
                    "max": normal_range["max"] if normal_range else 0,
                    "unit": normal_range["unit"] if normal_range else param.unit
                } if normal_range else None,
                "risk_level": risk_level,
                "explanation": explanation,
                "lifestyle_recommendations": [],  # Can be added later
                "extracted_at": datetime.utcnow()
            }
            
            parameter_docs.append(param_doc)
            logger.info(f"  {param.name}: {param.value} {param.unit} - {risk_level}")
        
        # STEP 5: Store parameters in database
        logger.info("Step 5: Storing parameters...")
        if parameter_docs:
            await database.parameters.insert_many(parameter_docs)
        
        # Generate overall summary
        normal_count = sum(1 for p in parameter_docs if p["risk_level"] == "Normal")
        mild_count = sum(1 for p in parameter_docs if p["risk_level"] == "Mild Abnormal")
        critical_count = sum(1 for p in parameter_docs if p["risk_level"] == "Critical")
        
        summary = f"Analysis complete: {len(parameter_docs)} parameters detected. "
        summary += f"{normal_count} normal, {mild_count} mildly abnormal, {critical_count} critical. "
        
        if critical_count > 0:
            summary += "Some values require immediate medical attention. Consult your doctor immediately. "
        elif mild_count > 0:
            summary += "Some values are slightly outside normal range. Discuss with your doctor. "
        else:
            summary += "All detected values are within normal ranges. "
        
        summary += "This is not medical advice."
        
        # Update report status to completed
        await database.reports.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": {
                    "processing_status": "completed",
                    "summary": summary,
                    "processing_completed_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Processing complete for report {report_id}")
        return True
        
    except Exception as e:
        logger.error(f"Processing failed for report {report_id}: {e}", exc_info=True)
        
        try:
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "An error occurred during processing. Please try again or contact support.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
        except Exception:
            pass
        
        return False
