"""
Simple Parameter Extractor - Regex-based extraction for MVP
Uses regex patterns to quickly extract medical parameters without AI models.
This is a fast, working solution that can be enhanced with NER later.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedParameter:
    """Simple parameter data structure."""
    name: str
    value: float
    unit: str
    raw_text: str
    confidence: float = 0.9  # High confidence for regex matches


# Medical parameter patterns (parameter_name: [regex_patterns])
PARAMETER_PATTERNS = {
    "hemoglobin": [
        r"(?:hemoglobin|hb|hgb)[\s:]*(\d+\.?\d*)\s*(g/dl|g/l|gm/dl)",
        r"hb[\s:]*(\d+\.?\d*)\s*(g/dl|g/l)",
    ],
    "wbc": [
        r"(?:wbc|white blood cell|leukocyte)s?[\s:]*(\d+\.?\d*)\s*(?:x\s*10\^?3|k|thousand)?[\s/]*(μl|ul|cells/μl|/μl)",
        r"wbc[\s:]*(\d+\.?\d*)\s*k?",
    ],
    "platelets": [
        r"(?:platelet|plt)s?[\s:]*(\d+\.?\d*)\s*(?:x\s*10\^?3|k|thousand)?[\s/]*(μl|ul|/μl)",
        r"plt[\s:]*(\d+\.?\d*)\s*k?",
    ],
    "glucose": [
        r"(?:glucose|blood sugar|fasting glucose|fbs)[\s:]*(\d+\.?\d*)\s*(mg/dl|mmol/l)",
        r"glucose[\s:]*(\d+\.?\d*)",
    ],
    "cholesterol": [
        r"(?:total cholesterol|cholesterol|chol)[\s:]*(\d+\.?\d*)\s*(mg/dl|mmol/l)",
        r"cholesterol[\s:]*(\d+\.?\d*)",
    ],
    "ldl": [
        r"ldl[\s:]*(\d+\.?\d*)\s*(mg/dl|mmol/l)",
    ],
    "hdl": [
        r"hdl[\s:]*(\d+\.?\d*)\s*(mg/dl|mmol/l)",
    ],
    "triglycerides": [
        r"triglycerides?[\s:]*(\d+\.?\d*)\s*(mg/dl|mmol/l)",
    ],
    "tsh": [
        r"tsh[\s:]*(\d+\.?\d*)\s*(μiu/ml|miu/l|uiu/ml)",
    ],
    "alt": [
        r"(?:alt|sgpt)[\s:]*(\d+\.?\d*)\s*(u/l|iu/l)",
    ],
    "ast": [
        r"(?:ast|sgot)[\s:]*(\d+\.?\d*)\s*(u/l|iu/l)",
    ],
    "creatinine": [
        r"creatinine[\s:]*(\d+\.?\d*)\s*(mg/dl|μmol/l|umol/l)",
    ],
}


# Hardcoded normal ranges (can be moved to database later)
NORMAL_RANGES = {
    "hemoglobin": {
        "male": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
        "female": {"min": 12.0, "max": 15.5, "unit": "g/dL"},
    },
    "wbc": {
        "male": {"min": 4.5, "max": 11.0, "unit": "k/μL"},
        "female": {"min": 4.5, "max": 11.0, "unit": "k/μL"},
    },
    "platelets": {
        "male": {"min": 150, "max": 400, "unit": "k/μL"},
        "female": {"min": 150, "max": 400, "unit": "k/μL"},
    },
    "glucose": {
        "male": {"min": 70, "max": 100, "unit": "mg/dL"},
        "female": {"min": 70, "max": 100, "unit": "mg/dL"},
    },
    "cholesterol": {
        "male": {"min": 0, "max": 200, "unit": "mg/dL"},
        "female": {"min": 0, "max": 200, "unit": "mg/dL"},
    },
    "ldl": {
        "male": {"min": 0, "max": 100, "unit": "mg/dL"},
        "female": {"min": 0, "max": 100, "unit": "mg/dL"},
    },
    "hdl": {
        "male": {"min": 40, "max": 999, "unit": "mg/dL"},
        "female": {"min": 50, "max": 999, "unit": "mg/dL"},
    },
    "triglycerides": {
        "male": {"min": 0, "max": 150, "unit": "mg/dL"},
        "female": {"min": 0, "max": 150, "unit": "mg/dL"},
    },
    "tsh": {
        "male": {"min": 0.4, "max": 4.0, "unit": "μIU/mL"},
        "female": {"min": 0.4, "max": 4.0, "unit": "μIU/mL"},
    },
    "alt": {
        "male": {"min": 7, "max": 56, "unit": "U/L"},
        "female": {"min": 7, "max": 56, "unit": "U/L"},
    },
    "ast": {
        "male": {"min": 10, "max": 40, "unit": "U/L"},
        "female": {"min": 10, "max": 40, "unit": "U/L"},
    },
    "creatinine": {
        "male": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
        "female": {"min": 0.6, "max": 1.1, "unit": "mg/dL"},
    },
}


def extract_parameters(text: str) -> List[ExtractedParameter]:
    """
    Extract medical parameters from text using regex patterns.
    
    Args:
        text: OCR-extracted text from lab report
        
    Returns:
        List of ExtractedParameter objects
    """
    if not text:
        return []
    
    # Normalize text for better matching
    text_lower = text.lower()
    
    parameters = []
    
    for param_name, patterns in PARAMETER_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            
            for match in matches:
                try:
                    # Extract value and unit
                    value_str = match.group(1)
                    value = float(value_str)
                    
                    # Extract unit if present
                    unit = match.group(2) if match.lastindex >= 2 else ""
                    
                    # Get the raw matched text
                    raw_text = match.group(0)
                    
                    # Create parameter object
                    param = ExtractedParameter(
                        name=param_name,
                        value=value,
                        unit=unit.strip(),
                        raw_text=raw_text,
                        confidence=0.9
                    )
                    
                    parameters.append(param)
                    logger.info(f"Extracted {param_name}: {value} {unit}")
                    
                    # Only take first match for each parameter
                    break
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse match for {param_name}: {e}")
                    continue
            
            # If we found a match, don't try other patterns for this parameter
            if any(p.name == param_name for p in parameters):
                break
    
    logger.info(f"Extracted {len(parameters)} parameters total")
    return parameters


def classify_risk(param_name: str, value: float, gender: str = "male") -> str:
    """
    Classify risk level based on normal ranges.
    
    Args:
        param_name: Parameter name
        value: Parameter value
        gender: Patient gender (male/female)
        
    Returns:
        Risk level: "Normal", "Mild Abnormal", or "Critical"
    """
    if param_name not in NORMAL_RANGES:
        return "Unknown"
    
    ranges = NORMAL_RANGES[param_name].get(gender.lower(), NORMAL_RANGES[param_name]["male"])
    min_val = ranges["min"]
    max_val = ranges["max"]
    
    # Check if within normal range
    if min_val <= value <= max_val:
        return "Normal"
    
    # Calculate deviation percentage
    if value < min_val:
        deviation = (min_val - value) / min_val
    else:
        deviation = (value - max_val) / max_val
    
    # Classify based on deviation
    if deviation < 0.20:  # Less than 20% deviation
        return "Mild Abnormal"
    else:
        return "Critical"


def get_normal_range(param_name: str, gender: str = "male") -> Optional[Dict]:
    """Get normal range for a parameter."""
    if param_name not in NORMAL_RANGES:
        return None
    return NORMAL_RANGES[param_name].get(gender.lower(), NORMAL_RANGES[param_name]["male"])


def generate_simple_explanation(param_name: str, value: float, risk_level: str, gender: str = "male") -> str:
    """
    Generate a simple explanation for a parameter.
    Template-based, no LLM needed for MVP.
    """
    range_info = get_normal_range(param_name, gender)
    
    if risk_level == "Normal":
        return f"Your {param_name} level of {value} is within the normal range. This is a good sign for your health. This is not medical advice. Consult your doctor for interpretation."
    
    elif risk_level == "Mild Abnormal":
        direction = "low" if range_info and value < range_info["min"] else "high"
        return f"Your {param_name} level of {value} is slightly {direction}. This may not be a serious concern, but you should discuss it with your doctor. This is not medical advice."
    
    elif risk_level == "Critical":
        direction = "low" if range_info and value < range_info["min"] else "high"
        return f"Your {param_name} level of {value} is significantly {direction}. This requires medical attention. Consult your doctor immediately. This is not medical advice."
    
    else:
        return f"Your {param_name} level is {value}. We don't have enough information to assess this value. Please consult your doctor. This is not medical advice."
