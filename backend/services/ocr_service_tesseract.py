"""
OCR Service using Tesseract for text extraction from lab reports.

This service handles:
- Initialization of Tesseract OCR
- Text extraction from images and PDFs
- Image preprocessing for better OCR accuracy

Requirements: 14.3, 3.1, 3.5, 3.6
"""

import logging
from typing import List, Optional
from dataclasses import dataclass
import numpy as np
import cv2
from pathlib import Path
import pytesseract

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Represents a bounding box for detected text."""
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
    """Result from OCR text extraction."""
    text: str
    confidence: float
    bounding_boxes: List[BoundingBox]
    page_number: int = 1


class OCRService:
    """
    Service for extracting text from lab report images and PDFs using Tesseract.
    
    Configured for:
    - English language recognition
    - High accuracy mode
    - Stable Windows compatibility
    """
    
    def __init__(self, lang: str = 'eng'):
        """
        Initialize Tesseract OCR service.
        
        Args:
            lang: Language for OCR recognition (default: 'eng' for English)
        """
        self.lang = lang
        self._verify_tesseract()
    
    def _verify_tesseract(self):
        """Verify Tesseract is installed and accessible."""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR initialized successfully (version {version})")
        except Exception as e:
            logger.error(f"Tesseract not found: {e}")
            raise RuntimeError(
                "Tesseract OCR not installed. "
                "Download from: https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
    def extract_text(self, file_path: str) -> OCRResult:
        """
        Extract text from an image file with preprocessing.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            OCRResult containing extracted text, confidence, and bounding boxes
            
        Raises:
            RuntimeError: If OCR extraction fails
        """
        try:
            logger.info(f"Extracting text from: {file_path}")
            
            # Load and preprocess image
            image = cv2.imread(file_path)
            if image is None:
                raise RuntimeError(f"Failed to load image: {file_path}")
            
            preprocessed = self.preprocess_image(image)
            
            # Extract text with detailed data
            data = pytesseract.image_to_data(
                preprocessed,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )
            
            # Parse results
            extracted_lines = []
            bounding_boxes = []
            confidences = []
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                conf = int(data['conf'][i])
                
                # Skip empty text or low confidence
                if text and conf > 0:
                    extracted_lines.append(text)
                    confidences.append(conf)
                    
                    # Create bounding box
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    bbox = BoundingBox(
                        x1=float(x), y1=float(y),
                        x2=float(x + w), y2=float(y),
                        x3=float(x + w), y3=float(y + h),
                        x4=float(x), y4=float(y + h)
                    )
                    bounding_boxes.append(bbox)
            
            # Combine text
            full_text = " ".join(extracted_lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"Extracted {len(extracted_lines)} text segments with avg confidence {avg_confidence:.2f}")
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence / 100.0,  # Normalize to 0-1
                bounding_boxes=bounding_boxes,
                page_number=1
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {file_path}: {e}")
            raise RuntimeError(f"OCR extraction failed: {e}")
    
    def extract_from_image(self, image_path: str) -> OCRResult:
        """Extract text from an image file (JPEG, PNG)."""
        return self.extract_text(image_path)
    
    def extract_from_pdf(self, pdf_path: str) -> List[OCRResult]:
        """Extract text from all pages of a PDF file."""
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Convert PDF to images
            images = self._pdf_to_images(pdf_path)
            
            # Process each page
            results = []
            for page_num, image in enumerate(images, start=1):
                logger.info(f"Processing page {page_num}/{len(images)}")
                
                # Preprocess image
                preprocessed = self.preprocess_image(image)
                
                # Extract text
                data = pytesseract.image_to_data(
                    preprocessed,
                    lang=self.lang,
                    output_type=pytesseract.Output.DICT
                )
                
                # Parse results
                extracted_lines = []
                bounding_boxes = []
                confidences = []
                
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    text = data['text'][i].strip()
                    conf = int(data['conf'][i])
                    
                    if text and conf > 0:
                        extracted_lines.append(text)
                        confidences.append(conf)
                        
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        bbox = BoundingBox(
                            x1=float(x), y1=float(y),
                            x2=float(x + w), y2=float(y),
                            x3=float(x + w), y3=float(y + h),
                            x4=float(x), y4=float(y + h)
                        )
                        bounding_boxes.append(bbox)
                
                full_text = " ".join(extracted_lines)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                results.append(OCRResult(
                    text=full_text,
                    confidence=avg_confidence / 100.0,
                    bounding_boxes=bounding_boxes,
                    page_number=page_num
                ))
                
                logger.info(f"Page {page_num}: Extracted {len(extracted_lines)} segments")
            
            return results
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise RuntimeError(f"PDF extraction failed: {e}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy."""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Enhance contrast with CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Threshold to binary
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
            
        except Exception as e:
            logger.warning(f"Preprocessing failed: {e}, using original")
            return image
    
    def _pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to images."""
        try:
            from pdf2image import convert_from_path
            
            pil_images = convert_from_path(pdf_path, dpi=300, fmt='RGB')
            
            images = []
            for pil_img in pil_images:
                img_array = np.array(pil_img)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                images.append(img_bgr)
            
            logger.info(f"Converted {len(images)} pages from PDF")
            return images
            
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise RuntimeError(f"PDF conversion failed: {e}")
    
    def get_config(self) -> dict:
        """Get current OCR service configuration."""
        return {
            "lang": self.lang,
            "engine": "Tesseract",
            "initialized": True
        }


# Global OCR service instance
_ocr_service_instance: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Get or create the global OCR service instance."""
    global _ocr_service_instance
    
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService(lang='eng')
    
    return _ocr_service_instance
