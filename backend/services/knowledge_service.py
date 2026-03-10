"""
Knowledge Service for Medical Parameter Analysis

Requirements: 5.1-5.7, 7.1, 7.7, 9.1-9.8, 20.1-20.8
"""

import logging
from typing import Optional, List
from enum import Enum
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classification for medical parameters."""
    NORMAL = "Normal"
    MILD_ABNORMAL = "Mild Abnormal"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


@dataclass
class NormalRange:
    """Normal range for a medical parameter."""
    parameter: str
    min_value: float
    max_value: float
    unit: str
    age_range: str
    gender: str
    source: str = "Medical Database"


@dataclass
class ParameterClassification:
    """Complete classification of a medical parameter."""
    parameter_name: str
    value: float
    unit: str
    risk_level: RiskLevel
    deviation_percent: float
    normal_range: Optional[NormalRange]
    organ_system: str
    lifestyle_recommendations: List[str]
    medical_translation: Optional[str] = None


class KnowledgeService:
    """Service for medical knowledge operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.medical_ranges = db.medical_ranges
        self.medical_translations = db.medical_translations
        self.lifestyle_recommendations = db.lifestyle_recommendations
        logger.info("Knowledge Service initialized")
    
    async def get_normal_range(self, parameter: str, age: int, gender: str) -> Optional[NormalRange]:
        """Retrieve normal range for a parameter based on age and gender."""
        try:
            doc = await self.medical_ranges.find_one({"parameter": parameter})
            if not doc or "ranges" not in doc:
                return None
            
            for range_data in doc["ranges"]:
                age_min = range_data.get("age_min", 0)
                age_max = range_data.get("age_max", 999)
                range_gender = range_data.get("gender", "").lower()
                
                if age_min <= age <= age_max and range_gender == gender.lower():
                    return NormalRange(
                        parameter=parameter,
                        min_value=range_data["min_value"],
                        max_value=range_data["max_value"],
                        unit=range_data["unit"],
                        age_range=f"{age_min}-{age_max}",
                        gender=gender,
                        source=doc.get("source", "Medical Database")
                    )
            return None
        except Exception as e:
            logger.error(f"Error retrieving normal range: {e}")
            return None
    
    def classify_risk_level(self, value: float, normal_range: Optional[NormalRange]) -> tuple[RiskLevel, float]:
        """Classify risk level based on deviation from normal range."""
        if normal_range is None:
            return RiskLevel.UNKNOWN, 0.0
        
        if normal_range.min_value <= value <= normal_range.max_value:
            return RiskLevel.NORMAL, 0.0
        
        if value < normal_range.min_value:
            deviation = ((normal_range.min_value - value) / normal_range.min_value) * 100
        else:
            deviation = ((value - normal_range.max_value) / normal_range.max_value) * 100
        
        if deviation < 20.0:
            return RiskLevel.MILD_ABNORMAL, deviation
        else:
            return RiskLevel.CRITICAL, deviation
    
    async def get_medical_translation(self, medical_term: str) -> Optional[str]:
        """Get common language translation for a medical term."""
        try:
            doc = await self.medical_translations.find_one({"medical_term": medical_term})
            if doc and "common_term" in doc:
                return doc["common_term"]
            return None
        except Exception as e:
            logger.error(f"Error retrieving translation: {e}")
            return None
    
    async def get_lifestyle_recommendations(self, parameter: str, risk_level: RiskLevel) -> List[str]:
        """Get lifestyle recommendations for a parameter and risk level."""
        try:
            doc = await self.lifestyle_recommendations.find_one({
                "parameter": parameter,
                "risk_level": risk_level.value
            })
            if doc and "recommendations" in doc:
                return doc["recommendations"]
            return []
        except Exception as e:
            logger.error(f"Error retrieving recommendations: {e}")
            return []
    
    async def get_organ_system(self, parameter: str) -> str:
        """Get the organ system associated with a parameter."""
        organ_systems = {
            "hemoglobin": "Hematology",
            "wbc": "Hematology",
            "platelets": "Hematology",
            "glucose": "Endocrine/Metabolic",
            "cholesterol": "Cardiovascular",
            "tsh": "Endocrine",
            "alt": "Hepatic",
            "ast": "Hepatic",
            "creatinine": "Renal"
        }
        return organ_systems.get(parameter, "General")
    
    async def classify_parameter(self, parameter_name: str, value: float, unit: str, age: int, gender: str) -> ParameterClassification:
        """Complete classification of a medical parameter."""
        normal_range = await self.get_normal_range(parameter_name, age, gender)
        risk_level, deviation = self.classify_risk_level(value, normal_range)
        organ_system = await self.get_organ_system(parameter_name)
        recommendations = await self.get_lifestyle_recommendations(parameter_name, risk_level)
        
        return ParameterClassification(
            parameter_name=parameter_name,
            value=value,
            unit=unit,
            risk_level=risk_level,
            deviation_percent=deviation,
            normal_range=normal_range,
            organ_system=organ_system,
            lifestyle_recommendations=recommendations
        )


# Singleton instance
_knowledge_service: Optional[KnowledgeService] = None


def get_knowledge_service(db: AsyncIOMotorDatabase) -> KnowledgeService:
    """
    Get or create the Knowledge Service instance.
    
    Args:
        db: MongoDB database instance
    
    Returns:
        KnowledgeService instance
    """
    global _knowledge_service
    
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService(db)
    
    return _knowledge_service
