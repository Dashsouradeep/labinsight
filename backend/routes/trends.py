"""
Trends API Routes

Provides endpoints for accessing trend analysis data.

Requirements: 15.8
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from middleware.auth import get_current_user
from database import get_database
from services.trend_analysis_service import get_trend_service
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("")
async def get_trends(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get trend analysis for all parameters for the authenticated user.
    
    Requirements: 15.8
    
    Returns:
        Dictionary with trend analysis for each parameter
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Fetching trends for user {user_id}")
        
        # Get all reports for the user, sorted by upload date
        reports_cursor = db.reports.find(
            {"user_id": user_id, "processing_status": "completed"}
        ).sort("upload_date", 1)
        
        reports = await reports_cursor.to_list(length=None)
        
        if len(reports) < 2:
            return {
                "user_id": user_id,
                "parameters": [],
                "generated_at": datetime.utcnow().isoformat(),
                "report_count": len(reports),
                "message": "Need at least 2 reports to analyze trends"
            }
        
        # Get parameters for each report
        reports_data = []
        for report in reports:
            report_id = report["_id"]
            
            # Get parameters for this report
            parameters_cursor = db.parameters.find({"report_id": report_id})
            parameters = await parameters_cursor.to_list(length=None)
            
            # Format parameters
            formatted_params = []
            for param in parameters:
                formatted_params.append({
                    "name": param.get("parameter_name", ""),
                    "value": param.get("value", 0.0),
                    "unit": param.get("unit", ""),
                    "risk_level": param.get("risk_level", "Unknown"),
                    "normal_range": (
                        param.get("normal_range", {}).get("min"),
                        param.get("normal_range", {}).get("max")
                    ) if param.get("normal_range") else None
                })
            
            reports_data.append({
                "_id": str(report_id),
                "upload_date": report.get("upload_date", datetime.utcnow()),
                "parameters": formatted_params
            })
        
        # Analyze trends
        trend_service = get_trend_service()
        trends = trend_service.analyze_all_trends(reports_data)
        
        # Format response to match frontend expectations
        parameters_list = []
        for param_name, analysis in trends.items():
            parameters_list.append({
                "parameter_name": analysis.parameter_name,
                "trend_direction": analysis.trend_direction.value,
                "change_percent": round(analysis.change_percent, 2),
                "summary": analysis.summary,
                "data_points": [
                    {
                        "report_id": dp.report_id,
                        "date": dp.date.isoformat(),
                        "value": dp.value,
                        "unit": dp.unit,
                        "risk_level": dp.risk_level,
                        "normal_range": {
                            "min": dp.normal_range[0],
                            "max": dp.normal_range[1]
                        } if dp.normal_range else None
                    }
                    for dp in analysis.data_points
                ]
            })
        
        logger.info(f"Returning trends for {len(parameters_list)} parameters")
        
        return {
            "user_id": user_id,
            "parameters": parameters_list,
            "generated_at": datetime.utcnow().isoformat(),
            "report_count": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Error fetching trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch trends")


@router.get("/{parameter_name}")
async def get_parameter_trend(
    parameter_name: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get trend analysis for a specific parameter.
    
    Args:
        parameter_name: Name of the parameter to analyze
    
    Returns:
        Trend analysis for the specified parameter
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Fetching trend for {parameter_name} for user {user_id}")
        
        # Get all reports for the user
        reports_cursor = db.reports.find(
            {"user_id": user_id, "processing_status": "completed"}
        ).sort("upload_date", 1)
        
        reports = await reports_cursor.to_list(length=None)
        
        if len(reports) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 reports to analyze trends"
            )
        
        # Get parameters for each report
        reports_data = []
        for report in reports:
            report_id = report["_id"]
            
            # Get parameters for this report
            parameters_cursor = db.parameters.find({"report_id": report_id})
            parameters = await parameters_cursor.to_list(length=None)
            
            # Format parameters
            formatted_params = []
            for param in parameters:
                formatted_params.append({
                    "name": param.get("parameter_name", ""),
                    "value": param.get("value", 0.0),
                    "unit": param.get("unit", ""),
                    "risk_level": param.get("risk_level", "Unknown"),
                    "normal_range": (
                        param.get("normal_range", {}).get("min"),
                        param.get("normal_range", {}).get("max")
                    ) if param.get("normal_range") else None
                })
            
            reports_data.append({
                "_id": str(report_id),
                "upload_date": report.get("upload_date", datetime.utcnow()),
                "parameters": formatted_params
            })
        
        # Analyze trend for specific parameter
        trend_service = get_trend_service()
        analysis = trend_service.analyze_parameter_trend(parameter_name, reports_data)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No trend data found for parameter: {parameter_name}"
            )
        
        # Format response
        return {
            "parameter_name": analysis.parameter_name,
            "trend_direction": analysis.trend_direction.value,
            "change_percent": round(analysis.change_percent, 2),
            "summary": analysis.summary,
            "data_points": [
                {
                    "report_id": dp.report_id,
                    "date": dp.date.isoformat(),
                    "value": dp.value,
                    "unit": dp.unit,
                    "risk_level": dp.risk_level,
                    "normal_range": {
                        "min": dp.normal_range[0],
                        "max": dp.normal_range[1]
                    } if dp.normal_range else None
                }
                for dp in analysis.data_points
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trend for {parameter_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch trend")
