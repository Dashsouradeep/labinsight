"""
Temporary Mock OCR Service - allows system to start without PaddleOCR
This will be replaced with the real OCR service once dependencies are installed.
"""

import logging
from typing import List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    x4: float
    y4: float


@dataclass
class OCRResult:
    text: str
    confidence: float
    bounding_boxes: List[BoundingBox]
    page_number: int = 1


class OCRService:
    """Mock OCR Service - returns sample text for testing"""
    
    def __init__(self, use_gpu: bool = True, lang: str = 'en'):
        self.lang = lang
        self.use_gpu = use_gpu
        logger.info("Mock OCR Service initialized (PaddleOCR not available)")
    
    def extract_from_image(self, image_path: str) -> OCRResult:
        """Returns sample lab report text"""
        sample_text = """LABORATORY REPORT
Patient: John Doe
Date: 2024-01-15

TEST RESULTS:
Hemoglobin: 14.5 g/dL
WBC Count: 7200 /µL
Platelet Count: 250000 /µL
Glucose: 95 mg/dL
Cholesterol: 180 mg/dL"""
        
        return OCRResult(
            text=sample_text,
            confidence=0.95,
            bounding_boxes=[],
            page_number=1
        )
    
    def extract_from_pdf(self, pdf_path: str) -> List[OCRResult]:
        """Returns sample lab report text for PDF"""
        return [self.extract_from_image(pdf_path)]


def get_ocr_service() -> OCRService:
    """Get mock OCR service instance"""
    return OCRService()
