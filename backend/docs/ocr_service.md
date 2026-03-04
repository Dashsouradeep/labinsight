# OCR Service Documentation

## Overview

The OCR Service provides text extraction capabilities for lab report images and PDFs using PaddleOCR. It is configured for English language recognition with GPU acceleration and automatic CPU fallback.

## Features

- **PaddleOCR Integration**: Uses PaddleOCR 2.7.0 for high-accuracy text recognition
- **GPU Acceleration**: Configured to use GPU when available, with automatic CPU fallback
- **English Language Support**: Optimized for English medical lab reports
- **Bounding Box Detection**: Returns text location information for each detected line
- **Confidence Scoring**: Provides confidence scores for extracted text
- **Angle Classification**: Handles rotated text in images

## Installation

The required packages are already included in `requirements.txt`:

```
paddleocr==2.7.0
paddlepaddle==2.5.2
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### GPU vs CPU

The service automatically detects GPU availability:

- **GPU Mode**: Uses CUDA acceleration for faster processing (requires CUDA-compatible GPU)
- **CPU Mode**: Falls back to CPU if GPU is unavailable or initialization fails

### Language Support

Currently configured for English (`lang='en'`). PaddleOCR supports multiple languages if needed in the future.

## Usage

### Basic Usage

```python
from services.ocr_service import get_ocr_service

# Get the OCR service instance
ocr_service = get_ocr_service()

# Extract text from an image
result = ocr_service.extract_text("path/to/lab_report.jpg")

print(f"Extracted Text: {result.text}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Lines Detected: {len(result.bounding_boxes)}")
```

### Extract from Image

```python
# Extract from JPEG or PNG image
result = ocr_service.extract_from_image("uploads/report.jpg")

# Access extracted text
full_text = result.text

# Access individual bounding boxes
for bbox in result.bounding_boxes:
    print(f"Text location: ({bbox.x1}, {bbox.y1}) to ({bbox.x3}, {bbox.y3})")
```

### Extract from PDF (Future)

```python
# Multi-page PDF extraction (to be implemented)
results = ocr_service.extract_from_pdf("uploads/report.pdf")

for page_num, result in enumerate(results, 1):
    print(f"Page {page_num}: {len(result.text)} characters")
```

### Check Configuration

```python
config = ocr_service.get_config()
print(f"Language: {config['lang']}")
print(f"GPU Enabled: {config['use_gpu']}")
print(f"Initialized: {config['initialized']}")
```

## Data Models

### OCRResult

```python
@dataclass
class OCRResult:
    text: str                      # Full extracted text
    confidence: float              # Average confidence score (0.0 to 1.0)
    bounding_boxes: List[BoundingBox]  # Text location information
    page_number: int = 1           # Page number (for multi-page documents)
```

### BoundingBox

```python
@dataclass
class BoundingBox:
    x1: float  # Top-left x
    y1: float  # Top-left y
    x2: float  # Top-right x
    y2: float  # Top-right y
    x3: float  # Bottom-right x
    y3: float  # Bottom-right y
    x4: float  # Bottom-left x
    y4: float  # Bottom-left y
```

## Error Handling

The service includes comprehensive error handling:

```python
try:
    result = ocr_service.extract_text("path/to/image.jpg")
except RuntimeError as e:
    print(f"OCR failed: {e}")
    # Handle error (log, notify user, etc.)
```

Common errors:
- **OCR engine not initialized**: Service failed to initialize PaddleOCR
- **OCR extraction failed**: File not found, corrupted image, or unsupported format
- **No text detected**: Image contains no recognizable text

## Performance Considerations

### GPU vs CPU Performance

- **GPU Mode**: ~2-5 seconds per page (typical lab report)
- **CPU Mode**: ~5-15 seconds per page (typical lab report)

### Memory Requirements

- **GPU Mode**: Requires ~2-4GB GPU memory
- **CPU Mode**: Requires ~1-2GB RAM

### Optimization Tips

1. **Image Quality**: Higher resolution images (300 DPI) provide better accuracy
2. **File Format**: JPEG and PNG are directly supported
3. **Preprocessing**: For low-quality images, consider preprocessing (deskew, denoise)
4. **Batch Processing**: Process multiple images sequentially to reuse loaded models

## Integration with Processing Pipeline

The OCR service is part of the report processing pipeline:

```
Upload → OCR Service → NER Service → Knowledge Service → LLM Service → Trend Analysis
```

### Pipeline Integration Example

```python
from services.ocr_service import get_ocr_service
from database import get_database

async def process_report(report_id: str):
    db = await get_database()
    
    # Get report from database
    report = await db.reports.find_one({"_id": report_id})
    
    # Extract text using OCR
    ocr_service = get_ocr_service()
    result = ocr_service.extract_text(report["file_path"])
    
    # Store extracted text
    await db.reports.update_one(
        {"_id": report_id},
        {"$set": {
            "ocr_text": result.text,
            "ocr_confidence": result.confidence,
            "processing_status": "ocr_complete"
        }}
    )
    
    # Trigger next stage (NER)
    # ... continue pipeline
```

## Troubleshooting

### GPU Not Detected

If GPU is available but not being used:

1. Check CUDA installation: `nvidia-smi`
2. Verify PaddlePaddle GPU version: `python -c "import paddle; print(paddle.device.is_compiled_with_cuda())"`
3. Check logs for GPU initialization errors

### Low Accuracy

If OCR accuracy is poor:

1. Check image quality (resolution, contrast, clarity)
2. Ensure text is not rotated (angle classification should handle this)
3. Consider image preprocessing for low-quality scans
4. Verify language setting matches document language

### Memory Issues

If running out of memory:

1. Reduce batch size (process one image at a time)
2. Use CPU mode instead of GPU
3. Close other applications using GPU memory
4. Consider using a machine with more RAM/GPU memory

## Future Enhancements

Planned improvements for the OCR service:

1. **PDF Multi-Page Support**: Convert PDF pages to images and process sequentially
2. **Image Preprocessing**: Implement deskew, denoise, and contrast enhancement
3. **Table Detection**: Identify and extract tabular data from lab reports
4. **Layout Analysis**: Preserve document structure and formatting
5. **Confidence Thresholding**: Filter low-confidence results
6. **Batch Processing**: Process multiple documents in parallel

## Requirements Validation

This service validates the following requirements:

- **Requirement 14.3**: PaddleOCR configured for English language and GPU usage
- **Requirement 3.1**: Extract all visible text from documents
- **Requirement 3.5**: Extract text from multi-page PDFs (planned)
- **Requirement 3.6**: Image preprocessing for improved accuracy (planned)

## Related Documentation

- [File Storage Service](./file_storage.md)
- [File Validation Service](./file_validation.md)
- [Processing Pipeline](./processing_pipeline.md) (to be created)
- [NER Service](./ner_service.md) (to be created)
