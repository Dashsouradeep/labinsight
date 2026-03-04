"""
NER Service for Medical Parameter Extraction using BioClinicalBERT

This service uses the BioClinicalBERT model from HuggingFace to extract
medical parameters from lab report text. BioClinicalBERT is a specialized
BERT model trained on clinical text, making it ideal for medical NER tasks.

Requirements: 14.2
"""

import logging
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
import torch
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline
)

logger = logging.getLogger(__name__)


# Task 7.2: Parameter name normalization mapping
# Maps various medical term variations to standardized parameter names
PARAMETER_NAME_MAPPING = {
    # Hemoglobin variations
    "hemoglobin": "hemoglobin",
    "hb": "hemoglobin",
    "hgb": "hemoglobin",
    "haemoglobin": "hemoglobin",
    
    # White Blood Cell variations
    "wbc": "wbc",
    "white blood cell": "wbc",
    "white blood cells": "wbc",
    "leukocyte": "wbc",
    "leukocytes": "wbc",
    "leucocyte": "wbc",
    
    # Platelet variations
    "platelet": "platelets",
    "platelets": "platelets",
    "plt": "platelets",
    "thrombocyte": "platelets",
    
    # Cholesterol variations
    "cholesterol": "cholesterol",
    "chol": "cholesterol",
    "total cholesterol": "cholesterol",
    
    # Glucose variations
    "glucose": "glucose",
    "blood sugar": "glucose",
    "blood glucose": "glucose",
    "fasting glucose": "glucose",
    "fbs": "glucose",
    "fasting blood sugar": "glucose",
    
    # TSH variations
    "tsh": "tsh",
    "thyroid stimulating hormone": "tsh",
    "thyrotropin": "tsh",
    
    # ALT variations
    "alt": "alt",
    "sgpt": "alt",
    "alanine aminotransferase": "alt",
    "alanine transaminase": "alt",
    
    # AST variations
    "ast": "ast",
    "sgot": "ast",
    "aspartate aminotransferase": "ast",
    "aspartate transaminase": "ast",
    
    # Creatinine variations
    "creatinine": "creatinine",
    "creat": "creatinine",
    "cr": "creatinine",
}

# Supported parameters list
SUPPORTED_PARAMETERS = [
    "hemoglobin", "wbc", "platelets", "cholesterol", 
    "glucose", "tsh", "alt", "ast", "creatinine"
]


@dataclass
class MedicalParameter:
    """
    Represents a medical parameter extracted from lab report text.
    
    Attributes:
        name: Normalized parameter name (e.g., "hemoglobin")
        value: Numeric value of the parameter
        unit: Unit of measurement (e.g., "g/dL")
        raw_text: Original text from which the parameter was extracted
        confidence: Confidence score of the extraction (0.0 to 1.0)
    """
    name: str
    value: float
    unit: str
    raw_text: str
    confidence: float


class NERService:
    """
    Named Entity Recognition service for extracting medical parameters
    from lab report text using BioClinicalBERT.
    
    The service loads the emilyalsentzer/Bio_ClinicalBERT model and tokenizer
    from HuggingFace and provides methods to extract structured medical
    parameters from unstructured text.
    """
    
    def __init__(self):
        """
        Initialize the NER service by loading BioClinicalBERT model and tokenizer.
        
        The model is loaded with GPU support if available, falling back to CPU.
        This initialization may take several seconds on first run as the model
        is downloaded from HuggingFace.
        
        Requirements: 14.2
        """
        logger.info("Initializing NER Service with BioClinicalBERT...")
        
        # Determine device (GPU if available, otherwise CPU)
        self.device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if self.device == 0 else "CPU"
        logger.info(f"Using device: {device_name}")
        
        # Model name from HuggingFace
        self.model_name = "emilyalsentzer/Bio_ClinicalBERT"
        
        try:
            # Load tokenizer
            logger.info(f"Loading tokenizer from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("Tokenizer loaded successfully")
            
            # Load model for token classification
            logger.info(f"Loading model from {self.model_name}...")
            self.model = AutoModelForTokenClassification.from_pretrained(
                self.model_name
            )
            logger.info("Model loaded successfully")
            
            # Move model to appropriate device
            if self.device == 0:
                self.model = self.model.cuda()
                logger.info("Model moved to GPU")
            
            # Create NER pipeline for easier inference
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
                aggregation_strategy="simple"
            )
            logger.info("NER pipeline created successfully")
            
            logger.info("NER Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NER Service: {str(e)}")
            raise RuntimeError(f"NER Service initialization failed: {str(e)}")
    
    def extract_parameters(self, text: str) -> List[MedicalParameter]:
        """
        Extract medical parameters from lab report text.
        
        This method uses the BioClinicalBERT model to identify medical entities
        in the text, then parses values and units to create structured
        MedicalParameter objects.
        
        Args:
            text: Raw text extracted from lab report (typically from OCR)
        
        Returns:
            List of MedicalParameter objects with extracted data
        
        Raises:
            ValueError: If text is empty or invalid
            RuntimeError: If NER inference fails
        
        Requirements: 4.1, 4.10, 4.11
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        logger.info(f"Extracting parameters from text (length: {len(text)} chars)")
        
        try:
            # Run NER inference
            entities = self.ner_pipeline(text)
            logger.info(f"Found {len(entities)} entities from NER model")
            
            parameters = []
            seen_parameters = set()  # Track to avoid duplicates
            
            for entity in entities:
                # Extract entity information
                entity_text = entity.get("word", "")
                entity_score = entity.get("score", 0.0)
                entity_start = entity.get("start", 0)
                
                logger.debug(f"Processing entity: {entity_text} (score: {entity_score})")
                
                # Normalize parameter name
                normalized_name = self.normalize_parameter_name(entity_text)
                
                if not normalized_name:
                    logger.debug(f"Entity '{entity_text}' not recognized as supported parameter")
                    continue
                
                # Skip if we've already extracted this parameter
                if normalized_name in seen_parameters:
                    logger.debug(f"Parameter '{normalized_name}' already extracted, skipping")
                    continue
                
                # Extract value and unit near this entity
                value, unit = self.extract_value_and_unit(text, entity_start)
                
                # Task 7.6: Handle extraction failures
                if value is None:
                    logger.warning(
                        f"Parameter '{normalized_name}' detected but no value found - marking as undetected"
                    )
                    continue  # Don't store invalid data
                
                # Create parameter object
                param = MedicalParameter(
                    name=normalized_name,
                    value=value,
                    unit=unit or "",
                    raw_text=entity_text,
                    confidence=entity_score
                )
                
                parameters.append(param)
                seen_parameters.add(normalized_name)
                
                logger.info(
                    f"Extracted parameter: {normalized_name} = {value} {unit} "
                    f"(confidence: {entity_score:.2f})"
                )
            
            logger.info(f"Successfully extracted {len(parameters)} medical parameters")
            return parameters
            
        except Exception as e:
            logger.error(f"Parameter extraction failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to extract parameters: {str(e)}")
    
    def identify_parameter_name(self, entity: str) -> Optional[str]:
        """
        Identify and normalize a parameter name from an extracted entity.
        
        Maps various medical term variations to standardized parameter names.
        For example: "Hb", "HGB", "Hemoglobin" all map to "hemoglobin".
        
        Args:
            entity: Raw entity text from NER model
        
        Returns:
            Normalized parameter name, or None if not recognized
        
        Requirements: 4.1
        """
        return self.normalize_parameter_name(entity)
    
    def extract_value_and_unit(
        self,
        text: str,
        entity_position: int
    ) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract numeric value and unit from text near an entity position.
        
        Uses regex patterns to find numeric values and units (e.g., "13.5 g/dL")
        in the vicinity of a detected medical parameter entity.
        
        Args:
            text: Full text containing the parameter
            entity_position: Character position of the entity in text
        
        Returns:
            Tuple of (value, unit) or (None, None) if not found
        
        Requirements: 4.1
        """
        # Define search window around entity (100 chars before and after)
        start = max(0, entity_position - 100)
        end = min(len(text), entity_position + 100)
        search_text = text[start:end]
        
        # Regex pattern for numeric value followed by optional unit
        # Matches: "13.5", "13.5 g/dL", "150 mg/dl", "4.5 x 10^3/μL"
        value_unit_pattern = r'(\d+\.?\d*)\s*(?:x\s*10\^?\d+)?\s*([a-zA-Z/μ]+)?'
        
        matches = list(re.finditer(value_unit_pattern, search_text))
        
        if not matches:
            return None, None
        
        # Find the match closest to the entity position
        entity_offset = entity_position - start
        closest_match = min(matches, key=lambda m: abs(m.start() - entity_offset))
        
        try:
            value = float(closest_match.group(1))
            unit = closest_match.group(2) if closest_match.lastindex >= 2 else ""
            
            # Clean up unit
            if unit:
                unit = unit.strip()
            
            return value, unit
            
        except (ValueError, IndexError):
            return None, None
    
    def normalize_parameter_name(self, raw_name: str) -> Optional[str]:
        """
        Normalize a raw parameter name to standard vocabulary.
        
        Converts various medical term variations to a consistent standard name.
        
        Args:
            raw_name: Raw parameter name from text
        
        Returns:
            Normalized parameter name, or None if not recognized
        
        Requirements: 4.1
        """
        if not raw_name:
            return None
        
        # Convert to lowercase for matching
        raw_lower = raw_name.lower().strip()
        
        # Look up in mapping
        normalized = PARAMETER_NAME_MAPPING.get(raw_lower)
        
        if normalized and normalized in SUPPORTED_PARAMETERS:
            return normalized
        
        return None
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model name, device, and status
        """
        return {
            "model_name": self.model_name,
            "device": "GPU" if self.device == 0 else "CPU",
            "tokenizer_vocab_size": len(self.tokenizer),
            "model_loaded": self.model is not None,
            "pipeline_ready": self.ner_pipeline is not None
        }


# Global NER service instance (lazy initialization)
_ner_service: Optional[NERService] = None


def get_ner_service() -> NERService:
    """
    Get or create the global NER service instance.
    
    This function implements lazy initialization to avoid loading the model
    until it's actually needed. The model is loaded once and reused for all
    subsequent requests.
    
    Returns:
        Initialized NERService instance
    
    Raises:
        RuntimeError: If service initialization fails
    """
    global _ner_service
    
    if _ner_service is None:
        logger.info("Creating NER service instance...")
        _ner_service = NERService()
    
    return _ner_service
