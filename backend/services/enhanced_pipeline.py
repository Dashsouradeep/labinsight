"""
Enhanced Processing Pipeline - Integrates All AI Services

Orchestrates: OCR → NER → Knowledge → LLM → Trend Analysis

Requirements: 16.1-16.9
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from services.ocr_service_tesseract import get_ocr_service
from services.ner_service import get_ner_service
from services.knowledge_service import get_knowledge_service
from services.llm_service import get_llm_service
from services.trend_analysis_service import get_trend_service

logger = logging.getLogger(__name__)


async def process_report_enhanced(
    report_id: str,
    database,
    user_age: int = 30,
    user_gender: str = "male"
) -> bool:
    """
    Enhanced end-to-end processing pipeline for a lab report.
    
    Pipeline Stages:
    1. OCR - Extract text from file
    2. NER - Extract parameters using BioClinicalBERT
    3. Knowledge - Classify risk levels and get ranges
    4. LLM - Generate explanations
    5. Trend - Analyze trends across reports
    
    Requirements: 16.1-16.9
    
    Args:
        report_id: Report ID to process
        database: Database connection
        user_age: User's age for range selection
        user_gender: User's gender for range selection
        
    Returns:
        True if successful, False otherwise
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Starting enhanced processing for report {report_id}")
        
        # Validate report ID
        if not ObjectId.is_valid(report_id):
            logger.error(f"Invalid report ID: {report_id}")
            return False
        
        # Get report from database
        report = await database.reports.find_one({"_id": ObjectId(report_id)})
        if not report:
            logger.error(f"Report not found: {report_id}")
            return False
        
        user_id = report.get("user_id")
        
        # Update status to processing
        await database.reports.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": {
                    "processing_status": "processing",
                    "processing_started_at": datetime.utcnow()
                }
            }
        )
        
        # STAGE 1: OCR - Extract text from file
        logger.info("Stage 1: Running OCR...")
        stage_start = datetime.utcnow()
        
        file_path = report.get("file_path")
        file_type = report.get("file_type", "")
        
        if not file_path:
            raise ValueError("No file path found")
        
        ocr_service = get_ocr_service()
        
        if file_type == "pdf":
            ocr_results = ocr_service.extract_from_pdf(file_path)
            extracted_text = "\n\n".join([
                f"Page {r.page_number}:\n{r.text}" 
                for r in ocr_results
            ])
        else:
            ocr_result = ocr_service.extract_from_image(file_path)
            extracted_text = ocr_result.text
        
        if not extracted_text or not extracted_text.strip():
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "No text could be extracted.",
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
        
        ocr_time = (datetime.utcnow() - stage_start).total_seconds()
        logger.info(f"OCR complete: {len(extracted_text)} chars in {ocr_time:.2f}s")
        
        # STAGE 2: NER - Extract parameters using BioClinicalBERT
        logger.info("Stage 2: Running NER (BioClinicalBERT)...")
        stage_start = datetime.utcnow()
        
        ner_service = get_ner_service()
        parameters = ner_service.extract_parameters(extracted_text)
        
        if not parameters:
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "completed",
                        "summary": "No medical parameters detected.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
            return True
        
        ner_time = (datetime.utcnow() - stage_start).total_seconds()
        logger.info(f"NER complete: {len(parameters)} parameters in {ner_time:.2f}s")
        
        # STAGE 3: Knowledge - Classify risk and get ranges
        logger.info("Stage 3: Running Knowledge Service...")
        stage_start = datetime.utcnow()
        
        knowledge_service = get_knowledge_service()
        classified_params = []
        
        for param in parameters:
            classification = knowledge_service.classify_parameter(
                param.name,
                param.value,
                user_age,
                user_gender
            )
            
            classified_params.append({
                "name": param.name,
                "value": param.value,
                "unit": param.unit,
                "classification": classification
            })
        
        knowledge_time = (datetime.utcnow() - stage_start).total_seconds()
        logger.info(f"Knowledge complete: {len(classified_params)} in {knowledge_time:.2f}s")
        
        # STAGE 4: LLM - Generate explanations
        logger.info("Stage 4: Running LLM Service...")
        stage_start = datetime.utcnow()
        
        llm_service = get_llm_service()
        parameter_docs = []
        
        for param_data in classified_params:
            param_name = param_data["name"]
            param_value = param_data["value"]
            param_unit = param_data["unit"]
            classification = param_data["classification"]
            
            # Generate explanation
            explanation = await llm_service.generate_explanation(
                parameter_name=param_name,
                value=param_value,
                unit=param_unit,
                normal_range=(
                    classification.normal_range.min_value,
                    classification.normal_range.max_value
                ) if classification.normal_range else None,
                risk_level=classification.risk_level
            )
            
            # Create parameter document
            param_doc = {
                "report_id": ObjectId(report_id),
                "user_id": user_id,
                "parameter_name": param_name,
                "value": param_value,
                "unit": param_unit,
                "normal_range": {
                    "min": classification.normal_range.min_value,
                    "max": classification.normal_range.max_value,
                    "unit": classification.normal_range.unit
                } if classification.normal_range else None,
                "risk_level": classification.risk_level.value,
                "explanation": explanation.explanation,
                "medical_translation": classification.medical_translation,
                "organ_system": classification.organ_system,
                "lifestyle_recommendations": classification.lifestyle_recommendations,
                "extracted_at": datetime.utcnow()
            }
            
            parameter_docs.append(param_doc)
        
        llm_time = (datetime.utcnow() - stage_start).total_seconds()
        logger.info(f"LLM complete: {len(parameter_docs)} in {llm_time:.2f}s")
        
        # Store parameters
        if parameter_docs:
            await database.parameters.insert_many(parameter_docs)
        
        # Generate summary
        summary_params = [
            {
                "name": p["parameter_name"],
                "value": p["value"],
                "unit": p["unit"],
                "risk_level": p["risk_level"]
            }
            for p in parameter_docs
        ]
        
        report_summary = await llm_service.generate_report_summary(summary_params)
        
        # STAGE 5: Trend Analysis
        logger.info("Stage 5: Running Trend Analysis...")
        stage_start = datetime.utcnow()
        
        # Get all completed reports for this user
        reports_cursor = database.reports.find(
            {"user_id": user_id, "processing_status": "completed"}
        ).sort("upload_date", 1)
        
        user_reports = await reports_cursor.to_list(length=None)
        
        if len(user_reports) >= 2:
            # Format reports data
            reports_data = []
            for r in user_reports:
                r_id = r["_id"]
                params_cursor = database.parameters.find({"report_id": r_id})
                params = await params_cursor.to_list(length=None)
                
                formatted_params = []
                for p in params:
                    formatted_params.append({
                        "name": p.get("parameter_name", ""),
                        "value": p.get("value", 0.0),
                        "unit": p.get("unit", ""),
                        "risk_level": p.get("risk_level", "Unknown"),
                        "normal_range": (
                            p.get("normal_range", {}).get("min"),
                            p.get("normal_range", {}).get("max")
                        ) if p.get("normal_range") else None
                    })
                
                reports_data.append({
                    "_id": str(r_id),
                    "upload_date": r.get("upload_date", datetime.utcnow()),
                    "parameters": formatted_params
                })
            
            # Analyze trends
            trend_service = get_trend_service()
            trends = trend_service.analyze_all_trends(reports_data)
            
            trend_time = (datetime.utcnow() - stage_start).total_seconds()
            logger.info(f"Trend analysis: {len(trends)} parameters in {trend_time:.2f}s")
        else:
            logger.info("Skipping trends: need at least 2 reports")
            trend_time = 0
        
        # Update report status
        total_time = (datetime.utcnow() - start_time).total_seconds()
        
        await database.reports.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": {
                    "processing_status": "completed",
                    "summary": report_summary.summary_text,
                    "processing_completed_at": datetime.utcnow(),
                    "processing_time_seconds": total_time,
                    "stage_times": {
                        "ocr": ocr_time,
                        "ner": ner_time,
                        "knowledge": knowledge_time,
                        "llm": llm_time,
                        "trend": trend_time
                    }
                }
            }
        )
        
        logger.info(f"Processing complete: {total_time:.2f}s")
        
        if total_time > 30:
            logger.warning(f"Slow pipeline: {total_time:.2f}s (target: <30s)")
        
        return True
        
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        
        try:
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "Processing error. Please try again.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
        except Exception:
            pass
        
        return False
