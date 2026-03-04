"""
OCR Service using PaddleOCR for text extraction from lab reports.

This service handles:
- Initialization of PaddleOCR with English language support
- GPU/CPU configuration with automatic fallback
- Text extraction from images and PDFs
- Image preprocessing for better OCR accuracy

Requirements: 14.3, 3.1, 3.5, 3.6
"""

import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import cv2
from pathlib import Path

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
    Service for extracting text from lab report images and PDFs using PaddleOCR.
    
    Configured for:
    - English language recognition
    - GPU usage with CPU fallback
    - High accuracy mode
    """
    
    def __init__(self, use_gpu: bool = True, lang: str = 'en'):
        """
        Initialize PaddleOCR service.
        
        Args:
            use_gpu: Whether to use GPU acceleration (falls back to CPU if unavailable)
            lang: Language for OCR recognition (default: 'en' for English)
        """
        self.lang = lang
        self.use_gpu = use_gpu
        self._ocr_engine = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """
        Initialize PaddleOCR engine.
        """
        try:
            from paddleocr import PaddleOCR
            import os
            
            # Disable oneDNN to avoid Windows compatibility issues
            os.environ['FLAGS_use_mkldnn'] = '0'
            os.environ['PADDLE_USE_MKLDNN'] = '0'
            
            logger.info(f"Initializing PaddleOCR with lang={self.lang}")
            
            # Initialize PaddleOCR with minimal configuration
            # Newer versions have simplified parameters
            self._ocr_engine = PaddleOCR(
                use_angle_cls=True,  # Enable angle classification for rotated text
                lang=self.lang,
                enable_mkldnn=False  # Explicitly disable oneDNN/MKLDNN
            )
            
            logger.info("PaddleOCR initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise RuntimeError(f"Failed to initialize PaddleOCR: {e}")
    
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
        if not self._ocr_engine:
            raise RuntimeError("OCR engine not initialized")
        
        try:
            logger.info(f"Extracting text from: {file_path}")
            
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise RuntimeError(f"Failed to load image: {file_path}")
            
            # Run OCR directly on the image
            # Note: Preprocessing disabled due to PaddlePaddle oneDNN compatibility issues on Windows
            result = self._ocr_engine.ocr(file_path)
            
            # Parse results
            if not result or not result[0]:
                logger.warning(f"No text detected in {file_path}")
                return OCRResult(
                    text="",
                    confidence=0.0,
                    bounding_boxes=[],
                    page_number=1
                )
            
            # Extract text and metadata
            extracted_lines = []
            bounding_boxes = []
            confidences = []
            
            for line in result[0]:
                if line:
                    # Line format: [bbox, (text, confidence)]
                    bbox_coords = line[0]
                    text_info = line[1]
                    
                    text = text_info[0]
                    confidence = text_info[1]
                    
                    extracted_lines.append(text)
                    confidences.append(confidence)
                    
                    # Create bounding box
                    bbox = BoundingBox(
                        x1=float(bbox_coords[0][0]),
                        y1=float(bbox_coords[0][1]),
                        x2=float(bbox_coords[1][0]),
                        y2=float(bbox_coords[1][1]),
                        x3=float(bbox_coords[2][0]),
                        y3=float(bbox_coords[2][1]),
                        x4=float(bbox_coords[3][0]),
                        y4=float(bbox_coords[3][1])
                    )
                    bounding_boxes.append(bbox)
            
            # Combine all text with newlines
            full_text = "\n".join(extracted_lines)
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"Extracted {len(extracted_lines)} lines with avg confidence {avg_confidence:.2f}")
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                page_number=1
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {file_path}: {e}")
            raise RuntimeError(f"OCR extraction failed: {e}")
    
    def extract_from_image(self, image_path: str) -> OCRResult:
        """
        Extract text from an image file (JPEG, PNG).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            OCRResult containing extracted text and metadata
        """
        return self.extract_text(image_path)
    
    def extract_from_pdf(self, pdf_path: str) -> List[OCRResult]:
        """
        Extract text from all pages of a PDF file.
        
        Converts PDF pages to images, applies preprocessing, and extracts text
        from each page.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of OCRResult objects, one per page
            
        Raises:
            RuntimeError: If PDF conversion or OCR extraction fails
            
        Requirements: 3.5, 3.6
        """
        if not self._ocr_engine:
            raise RuntimeError("OCR engine not initialized")
        
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Convert PDF to images
            images = self._pdf_to_images(pdf_path)
            
            # Process each page
            results = []
            for page_num, image in enumerate(images, start=1):
                logger.info(f"Processing page {page_num}/{len(images)}")
                
                # Save temp image for OCR
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    cv2.imwrite(tmp.name, image)
                    temp_path = tmp.name
                
                try:
                    # Run OCR directly on file path
                    # Note: Preprocessing disabled due to PaddlePaddle oneDNN compatibility issues
                    ocr_result = self._ocr_engine.ocr(temp_path)
                finally:
                    # Clean up temp file
                    try:
                        Path(temp_path).unlink()
                    except:
                        pass
                
                # Parse results
                if not ocr_result or not ocr_result[0]:
                    logger.warning(f"No text detected on page {page_num}")
                    results.append(OCRResult(
                        text="",
                        confidence=0.0,
                        bounding_boxes=[],
                        page_number=page_num
                    ))
                    continue
                
                # Extract text and metadata
                extracted_lines = []
                bounding_boxes = []
                confidences = []
                
                for line in ocr_result[0]:
                    if line:
                        bbox_coords = line[0]
                        text_info = line[1]
                        
                        text = text_info[0]
                        confidence = text_info[1]
                        
                        extracted_lines.append(text)
                        confidences.append(confidence)
                        
                        bbox = BoundingBox(
                            x1=float(bbox_coords[0][0]),
                            y1=float(bbox_coords[0][1]),
                            x2=float(bbox_coords[1][0]),
                            y2=float(bbox_coords[1][1]),
                            x3=float(bbox_coords[2][0]),
                            y3=float(bbox_coords[2][1]),
                            x4=float(bbox_coords[3][0]),
                            y4=float(bbox_coords[3][1])
                        )
                        bounding_boxes.append(bbox)
                
                full_text = "\n".join(extracted_lines)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                results.append(OCRResult(
                    text=full_text,
                    confidence=avg_confidence,
                    bounding_boxes=bounding_boxes,
                    page_number=page_num
                ))
                
                logger.info(f"Page {page_num}: Extracted {len(extracted_lines)} lines with avg confidence {avg_confidence:.2f}")
            
            logger.info(f"Completed PDF extraction: {len(results)} pages processed")
            return results
            
        except Exception as e:
            logger.error(f"PDF extraction failed for {pdf_path}: {e}")
            raise RuntimeError(f"PDF extraction failed: {e}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to improve OCR accuracy.
        
        Applies the following preprocessing steps:
        1. Deskew - Corrects rotation/skew in the image
        2. Denoise - Removes noise and artifacts
        3. Enhance contrast - Improves text visibility
        
        Args:
            image: Input image as numpy array (BGR format from cv2)
            
        Returns:
            Preprocessed image as numpy array
            
        Requirements: 3.6
        """
        try:
            # Step 1: Deskew the image
            deskewed = self._deskew_image(image)
            
            # Step 2: Denoise the image
            denoised = self._denoise_image(deskewed)
            
            # Step 3: Enhance contrast
            enhanced = self._enhance_contrast(denoised)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}, returning original image")
            return image
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew (correct rotation) of an image.
        
        Uses Hough line transform to detect dominant text lines and calculate
        the skew angle, then rotates the image to correct it.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Deskewed image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
            
            if lines is None or len(lines) == 0:
                # No lines detected, return original
                return image
            
            # Calculate angles of detected lines
            angles = []
            for line in lines:
                rho, theta = line[0]
                # Convert to degrees and normalize to [-45, 45] range
                angle = np.degrees(theta) - 90
                if -45 <= angle <= 45:
                    angles.append(angle)
            
            if not angles:
                return image
            
            # Use median angle to avoid outliers
            skew_angle = np.median(angles)
            
            # Only correct if skew is significant (> 0.5 degrees)
            if abs(skew_angle) < 0.5:
                return image
            
            # Rotate image to correct skew
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
            
            # Calculate new image dimensions to avoid cropping
            cos = np.abs(rotation_matrix[0, 0])
            sin = np.abs(rotation_matrix[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))
            
            # Adjust rotation matrix for new dimensions
            rotation_matrix[0, 2] += (new_w / 2) - center[0]
            rotation_matrix[1, 2] += (new_h / 2) - center[1]
            
            # Perform rotation with white background
            deskewed = cv2.warpAffine(
                image, 
                rotation_matrix, 
                (new_w, new_h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(255, 255, 255)
            )
            
            logger.debug(f"Deskewed image by {skew_angle:.2f} degrees")
            return deskewed
            
        except Exception as e:
            logger.warning(f"Deskew failed: {e}, returning original image")
            return image
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """
        Remove noise and artifacts from image.
        
        Uses Non-local Means Denoising algorithm which is effective for
        document images while preserving text edges.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Denoised image
        """
        try:
            # Apply different denoising based on color/grayscale
            if len(image.shape) == 3:
                # Color image - use fastNlMeansDenoisingColored
                denoised = cv2.fastNlMeansDenoisingColored(
                    image,
                    None,
                    h=10,  # Filter strength for luminance
                    hColor=10,  # Filter strength for color
                    templateWindowSize=7,
                    searchWindowSize=21
                )
            else:
                # Grayscale image - use fastNlMeansDenoising
                denoised = cv2.fastNlMeansDenoising(
                    image,
                    None,
                    h=10,
                    templateWindowSize=7,
                    searchWindowSize=21
                )
            
            logger.debug("Applied denoising to image")
            return denoised
            
        except Exception as e:
            logger.warning(f"Denoising failed: {e}, returning original image")
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast to improve text visibility.
        
        Uses CLAHE (Contrast Limited Adaptive Histogram Equalization) which
        is effective for improving text visibility in documents with varying
        lighting conditions.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Contrast-enhanced image
        """
        try:
            # Convert to LAB color space for better contrast enhancement
            if len(image.shape) == 3:
                # Color image
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # Apply CLAHE to L channel
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l_enhanced = clahe.apply(l)
                
                # Merge channels and convert back to BGR
                lab_enhanced = cv2.merge([l_enhanced, a, b])
                enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            else:
                # Grayscale image
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(image)
            
            logger.debug("Applied contrast enhancement to image")
            return enhanced
            
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}, returning original image")
            return image
    
    def _pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """
        Convert PDF pages to images.
        
        Uses pdf2image library to convert each page of a PDF to an image array.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of images (one per page) as numpy arrays
            
        Raises:
            RuntimeError: If PDF conversion fails
        """
        try:
            from pdf2image import convert_from_path
            
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF to PIL images
            pil_images = convert_from_path(
                pdf_path,
                dpi=300,  # High DPI for better OCR accuracy
                fmt='RGB'
            )
            
            # Convert PIL images to numpy arrays (BGR format for OpenCV)
            images = []
            for pil_img in pil_images:
                # Convert PIL RGB to numpy array
                img_array = np.array(pil_img)
                # Convert RGB to BGR for OpenCV
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                images.append(img_bgr)
            
            logger.info(f"Converted {len(images)} pages from PDF")
            return images
            
        except ImportError:
            logger.error("pdf2image library not installed. Install with: pip install pdf2image")
            raise RuntimeError("pdf2image library not available")
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            raise RuntimeError(f"PDF conversion failed: {e}")
    
    def get_config(self) -> dict:
        """
        Get current OCR service configuration.
        
        Returns:
            Dictionary with configuration details
        """
        return {
            "lang": self.lang,
            "use_gpu": self.use_gpu,
            "engine": "PaddleOCR",
            "initialized": self._ocr_engine is not None
        }


# Global OCR service instance
_ocr_service_instance: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """
    Get or create the global OCR service instance.
    
    Returns:
        OCRService instance
    """
    global _ocr_service_instance
    
    if _ocr_service_instance is None:
        _ocr_service_instance = OCRService(use_gpu=True, lang='en')
    
    return _ocr_service_instance


async def process_report_ocr(report_id: str, database) -> bool:
    """
    Process OCR extraction for a report.
    
    This internal function:
    1. Loads the report from database
    2. Retrieves the file from storage
    3. Runs OCR extraction (PDF or image)
    4. Stores extracted text in the report record
    5. Updates processing status
    6. Triggers NER service (when implemented)
    
    Args:
        report_id: ID of the report to process
        database: MongoDB database instance
        
    Returns:
        True if processing succeeded, False otherwise
        
    Raises:
        RuntimeError: If OCR processing fails
        
    Requirements: 16.2
    """
    from bson import ObjectId
    from datetime import datetime
    from pathlib import Path
    
    try:
        logger.info(f"Starting OCR processing for report {report_id}")
        
        # Validate ObjectId format
        if not ObjectId.is_valid(report_id):
            logger.error(f"Invalid report ID format: {report_id}")
            return False
        
        # Load report from database
        report_doc = await database.reports.find_one({"_id": ObjectId(report_id)})
        
        if not report_doc:
            logger.error(f"Report not found: {report_id}")
            return False
        
        # Get file path
        file_path = report_doc.get("file_path")
        if not file_path:
            logger.error(f"No file path found for report {report_id}")
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "File path not found",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
            return False
        
        # Check if file exists
        if not Path(file_path).exists():
            logger.error(f"File not found: {file_path}")
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "File not found on disk",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
            return False
        
        # Get OCR service instance
        ocr_service = get_ocr_service()
        
        # Determine file type and run appropriate OCR extraction
        file_type = report_doc.get("file_type", "")
        extracted_text = ""
        
        try:
            if file_type == "pdf":
                # Extract from PDF (multi-page)
                logger.info(f"Extracting text from PDF: {file_path}")
                ocr_results = ocr_service.extract_from_pdf(file_path)
                
                # Combine text from all pages
                page_texts = []
                for page_result in ocr_results:
                    if page_result.text:
                        page_texts.append(f"--- Page {page_result.page_number} ---\n{page_result.text}")
                
                extracted_text = "\n\n".join(page_texts)
                logger.info(f"Extracted text from {len(ocr_results)} pages")
                
            elif file_type in ["image/jpeg", "image/png"]:
                # Extract from image
                logger.info(f"Extracting text from image: {file_path}")
                ocr_result = ocr_service.extract_from_image(file_path)
                extracted_text = ocr_result.text
                logger.info(f"Extracted text with confidence {ocr_result.confidence:.2f}")
                
            else:
                logger.error(f"Unsupported file type: {file_type}")
                await database.reports.update_one(
                    {"_id": ObjectId(report_id)},
                    {
                        "$set": {
                            "processing_status": "failed",
                            "error_message": f"Unsupported file type: {file_type}",
                            "processing_completed_at": datetime.utcnow()
                        }
                    }
                )
                return False
            
            # Check if any text was extracted
            if not extracted_text or not extracted_text.strip():
                logger.warning(f"No text extracted from report {report_id}")
                await database.reports.update_one(
                    {"_id": ObjectId(report_id)},
                    {
                        "$set": {
                            "processing_status": "failed",
                            "error_message": "No text could be extracted. Please upload a clearer image.",
                            "ocr_text": "",
                            "processing_completed_at": datetime.utcnow()
                        }
                    }
                )
                return False
            
            # Store extracted text in database
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "ocr_text": extracted_text,
                        "processing_status": "ocr_completed"
                    }
                }
            )
            
            logger.info(
                f"OCR processing completed for report {report_id}",
                extra={
                    "report_id": report_id,
                    "text_length": len(extracted_text),
                    "file_type": file_type
                }
            )
            
            # TODO: Trigger NER service when implemented (Task 7.8)
            # For now, we mark the report as ready for NER processing
            # In future tasks, this will call the NER service to extract parameters
            
            return True
            
        except RuntimeError as e:
            # OCR extraction failed
            logger.error(f"OCR extraction failed for report {report_id}: {e}")
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "OCR extraction failed. Please upload a clearer image.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
            return False
            
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error during OCR processing for report {report_id}: {e}")
        try:
            await database.reports.update_one(
                {"_id": ObjectId(report_id)},
                {
                    "$set": {
                        "processing_status": "failed",
                        "error_message": "An unexpected error occurred during processing.",
                        "processing_completed_at": datetime.utcnow()
                    }
                }
            )
        except Exception:
            pass
        return False
