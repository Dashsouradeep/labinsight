# LabInsight Backend

FastAPI backend for the LabInsight health intelligence platform.

## Project Structure

```
backend/
├── api/                    # API endpoints
├── models/                 # Database models (Pydantic)
├── services/               # Business logic services
│   ├── auth_service.py    # Authentication
│   ├── ocr_service.py     # OCR with PaddleOCR
│   ├── ner_service.py     # NER with BioClinicalBERT
│   ├── llm_service.py     # LLM with Mistral 7B
│   ├── knowledge_service.py  # Medical knowledge
│   └── trend_service.py   # Trend analysis
├── tests/                  # Test files
├── config.py              # Configuration management
├── logging_config.py      # Structured logging
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## Running the Backend

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Run with Gunicorn (multiple workers)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Property-based tests only
pytest -m property

# Integration tests only
pytest -m integration

# Run with coverage
pytest --cov=. --cov-report=html
```

### Run Tests in Watch Mode

```bash
pytest-watch
```

## Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
# Required
JWT_SECRET_KEY=your-secret-key-here

# Optional (defaults provided)
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
```

## Services

### Auth Service
- User registration and login
- JWT token generation and validation
- Password hashing with bcrypt

### OCR Service
- Text extraction from PDFs and images
- Uses PaddleOCR
- Image preprocessing

### NER Service
- Medical parameter detection
- Uses BioClinicalBERT
- Parameter name normalization

### LLM Service
- Plain-language explanation generation
- Uses Mistral 7B via Ollama
- Medical disclaimer enforcement

### Knowledge Service
- Normal range retrieval
- Risk level classification
- Medical term translation
- Lifestyle recommendations

### Trend Analysis Service
- Multi-report comparison
- Trend direction detection
- Trend summary generation

## Logging

The application uses structured JSON logging. All logs include:

- `timestamp`: ISO 8601 format
- `level`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `logger`: Logger name
- `message`: Log message
- Additional context fields (user_id, report_id, etc.)

Example log entry:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "services.ocr_service",
  "message": "OCR extraction completed",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "report_id": "789e0123-e89b-12d3-a456-426614174000",
  "duration_ms": 2345
}
```

## Code Quality

### Linting

```bash
flake8 .
```

### Type Checking

```bash
mypy .
```

### Format Code

```bash
black .
isort .
```

## Database

### MongoDB Collections

- `users`: User accounts
- `reports`: Lab report metadata
- `parameters`: Extracted medical parameters
- `trend_history`: Trend analysis results
- `medical_ranges`: Normal range reference data
- `medical_translations`: Medical term translations
- `lifestyle_recommendations`: Lifestyle advice

### Indexes

Indexes are created automatically on:
- `users.email` (unique)
- `reports.user_id`
- `parameters.report_id`
- `parameters.user_id`
- `trend_history.user_id`
- `trend_history.parameter_name`

## AI Models

### PaddleOCR
- **Purpose**: Text extraction from documents
- **Language**: English
- **GPU**: Recommended for performance

### BioClinicalBERT
- **Purpose**: Medical entity recognition
- **Model**: emilyalsentzer/Bio_ClinicalBERT
- **Framework**: HuggingFace Transformers

### Mistral 7B
- **Purpose**: Explanation generation
- **Runtime**: Ollama
- **Model**: mistral:7b-instruct

## Performance

- **Target**: Process reports in <30 seconds
- **Concurrent Users**: 100+
- **Rate Limit**: 100 requests/minute per user
- **Database Query**: <100ms

## Security

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 24-hour expiration
- Input sanitization for XSS/SQL injection
- CORS configured for frontend domain
- Rate limiting per user
- User data isolation
