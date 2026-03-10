# LabInsight - AI-Powered Medical Lab Report Analysis Platform

> A comprehensive full-stack application that uses AI to analyze medical lab reports, extract parameters, provide explanations, and track health trends over time.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)](https://www.mongodb.com/)

## 🎯 Project Overview

LabInsight is an intelligent health platform that helps users understand their medical lab reports through AI-powered analysis. The system extracts medical parameters from uploaded reports, classifies risk levels, provides plain-language explanations, and tracks health trends over time.

### Key Features

- 📄 **OCR Text Extraction** - Extracts text from PDF and image lab reports using Tesseract OCR
- 🧠 **AI Parameter Detection** - Uses BioClinicalBERT for Named Entity Recognition to identify medical parameters
- 📊 **Risk Classification** - Automatically classifies parameters as Normal, Mild Abnormal, or Critical
- 💬 **Plain-Language Explanations** - Generates easy-to-understand explanations using Mistral 7B LLM
- 📈 **Trend Analysis** - Tracks parameter changes across multiple reports over time
- 🔐 **User Authentication** - Secure JWT-based authentication with session management
- 🎨 **Modern UI** - Responsive Next.js frontend with Tailwind CSS

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- MongoDB (Database)
- Redis (Caching & Session Management)
- Tesseract OCR (Text Extraction)
- BioClinicalBERT (NER)
- Mistral 7B via Ollama (LLM)

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- NextAuth.js
- SWR for data fetching
- Recharts for visualizations

**Testing:**
- Pytest with Hypothesis (Property-based testing)
- Jest & React Testing Library
- 2,920+ test cases across 23 properties

### System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│   MongoDB   │
│  (Next.js)  │      │   (FastAPI)  │      │  (Database) │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────▶ Redis (Cache)
                            │
                            ├─────▶ Tesseract (OCR)
                            │
                            ├─────▶ BioClinicalBERT (NER)
                            │
                            └─────▶ Ollama/Mistral (LLM)
```

### Processing Pipeline

```
Upload Report → OCR Extraction → NER Parameter Detection → 
Risk Classification → LLM Explanation → Trend Analysis → Display Results
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)
- 16GB RAM recommended
- GPU optional (for Ollama LLM)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Dashsouradeep/labinsight.git
cd labinsight
```

2. **Start with Docker Compose** (Easiest)
```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- Redis on port 6379
- Backend API on port 8000
- Frontend on port 3000

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup (Without Docker)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your configuration

# Start MongoDB and Redis locally
# (Install and run separately)

# Seed the database
python seed_database.py

# Run the backend
uvicorn main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Run the frontend
npm run dev
```

#### Ollama Setup (Optional - for LLM features)

```bash
# Install Ollama
# Visit: https://ollama.ai/download

# Pull Mistral model
ollama pull mistral

# Ollama will run on http://localhost:11434
```

## 📖 Usage

### 1. Create an Account
- Navigate to http://localhost:3000/auth/signup
- Enter email, password, age, and gender
- Accept the medical disclaimer

### 2. Upload a Lab Report
- Go to the Upload page
- Drag and drop a PDF or image of your lab report
- Supported formats: PDF, JPEG, PNG (max 10MB)

### 3. View Results
- The system processes your report automatically
- View extracted parameters with risk classifications
- Read AI-generated explanations in plain language
- See lifestyle recommendations

### 4. Track Trends
- Upload multiple reports over time
- View trend charts showing parameter changes
- See if values are improving, worsening, or stable

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Property-based tests
python -m pytest tests/test_*_properties*.py -v

# Frontend tests
cd frontend
npm test

# Run all tests with coverage
npm run test:coverage
```

### Test Coverage
- **23 property-based tests** with 2,920+ test cases
- Unit tests for all services
- Integration tests for API endpoints
- Frontend component tests

## 📁 Project Structure

```
labinsight/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── routes/                 # API endpoints
│   ├── services/               # Business logic
│   │   ├── ocr_service_tesseract.py
│   │   ├── ner_service.py
│   │   ├── knowledge_service.py
│   │   ├── llm_service.py
│   │   └── trend_analysis_service.py
│   ├── models/                 # Pydantic models
│   ├── tests/                  # Test files
│   ├── utils/                  # Error handling, retry logic
│   └── seed_data/              # Medical ranges & translations
├── frontend/
│   ├── app/                    # Next.js pages
│   ├── components/             # React components
│   ├── lib/                    # Utilities & API client
│   └── __tests__/              # Frontend tests
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

## 🎨 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Report Analysis
![Report Analysis](docs/screenshots/report-detail.png)

### Trend Charts
![Trends](docs/screenshots/trends.png)

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
MONGODB_URL=mongodb://localhost:27017/labinsight
REDIS_URL=redis://localhost:6379
OLLAMA_HOST=http://localhost:11434
JWT_SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-here
```

## 📊 Supported Medical Parameters

- Hemoglobin (Hb)
- White Blood Cell Count (WBC)
- Platelet Count
- Blood Glucose
- Cholesterol (Total, LDL, HDL)
- Thyroid Stimulating Hormone (TSH)
- Alanine Aminotransferase (ALT)
- Creatinine

## ⚠️ Medical Disclaimer

**IMPORTANT:** This application is for educational and informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## 🤝 Contributing

This is a portfolio/showcase project. Feel free to fork and adapt for your own use!

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Souradeep Dash**
- GitHub: https://github.com/Dashsouradeep
- LinkedIn: https://www.linkedin.com/in/souradeep-dash-98879525b/
- Email: dashsouradeep@gmail.com

## 🙏 Acknowledgments

- BioClinicalBERT by Emily Alsentzer
- Mistral AI for the LLM model
- Tesseract OCR by Google
- FastAPI and Next.js communities

## 📚 Documentation

For detailed documentation, see:
- [Setup Guide](SETUP.md)
- [Testing Guide](TESTING_GUIDE.md)
- [API Documentation](http://localhost:8000/docs) (when running)

## 🎯 Future Enhancements

- [ ] Support for more medical parameters
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Export reports as PDF
- [ ] Integration with health tracking devices
- [ ] Advanced analytics and insights

---

**Note:** This is a demonstration project showcasing full-stack development skills including:
- Modern web technologies (FastAPI, Next.js, TypeScript)
- AI/ML integration (OCR, NER, LLM)
- Database design and optimization
- Comprehensive testing (2,920+ test cases)
- Docker containerization
- Clean architecture and best practices
