# LabInsight Setup Guide

This guide will walk you through setting up the LabInsight platform for development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Docker & Docker Compose**: [Download Docker](https://www.docker.com/products/docker-desktop/)
- **Git**: [Download Git](https://git-scm.com/downloads)

### Hardware Requirements

- **RAM**: Minimum 16GB (for AI models)
- **GPU**: Minimum 8GB GPU memory (recommended for optimal performance)
- **Storage**: 20GB free space

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd labinsight
```

### 2. Start Infrastructure Services

Start MongoDB, Redis, and Ollama using Docker Compose:

```bash
docker-compose up -d
```

Wait for all services to start (this may take a minute):

```bash
docker-compose ps
```

All services should show "Up" status.

### 3. Download AI Models

Pull the Mistral 7B model (this will take 10-15 minutes depending on your internet speed):

```bash
docker exec -it labinsight-ollama ollama pull mistral:7b-instruct
```

Verify the model is downloaded:

```bash
docker exec -it labinsight-ollama ollama list
```

### 4. Setup Backend

#### Create Python Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- MongoDB and Redis drivers
- PaddleOCR and BioClinicalBERT (AI models)
- Pytest and Hypothesis (testing)
- And other dependencies

**Note**: Installing PaddleOCR and PyTorch may take 5-10 minutes.

#### Configure Environment Variables

```bash
cp .env.template .env
```

Edit `.env` and set a secure JWT secret key:

```bash
# Generate a secure random key (Linux/macOS)
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

Update the `JWT_SECRET_KEY` in `.env` with the generated key.

#### Create Upload Directory

```bash
mkdir -p uploads
```

#### Verify Backend Setup

Start the backend server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser. You should see:

```json
{
  "status": "healthy",
  "service": "LabInsight API",
  "version": "1.0.0"
}
```

Check the API documentation at http://localhost:8000/docs

Press `Ctrl+C` to stop the server.

### 5. Setup Frontend

Open a new terminal window and navigate to the frontend directory:

```bash
cd frontend
```

#### Install Node Dependencies

```bash
npm install
```

This will install:
- Next.js 14 (React framework)
- Tailwind CSS (styling)
- NextAuth.js (authentication)
- SWR (data fetching)
- Recharts (charts)
- And other dependencies

**Note**: This may take 3-5 minutes.

#### Configure Environment Variables

```bash
cp .env.local.template .env.local
```

Edit `.env.local` and set a secure NextAuth secret:

```bash
# Generate a secure random key
openssl rand -base64 32
```

Update the `NEXTAUTH_SECRET` in `.env.local` with the generated key.

#### Verify Frontend Setup

Start the development server:

```bash
npm run dev
```

Open http://localhost:3000 in your browser. You should see the LabInsight homepage.

Press `Ctrl+C` to stop the server.

### 6. Run Tests

#### Backend Tests

```bash
cd backend
source venv/bin/activate  # If not already activated
pytest
```

#### Frontend Tests

```bash
cd frontend
npm test
```

## Running the Complete Application

### Terminal 1: Infrastructure Services

```bash
docker-compose up
```

### Terminal 2: Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Frontend

```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: mongodb://localhost:27017
- **Redis**: redis://localhost:6379

## Troubleshooting

### Docker Services Won't Start

**Issue**: Port already in use

**Solution**: Check if MongoDB, Redis, or Ollama are already running:

```bash
# Check ports
lsof -i :27017  # MongoDB
lsof -i :6379   # Redis
lsof -i :11434  # Ollama

# Stop conflicting services or change ports in docker-compose.yml
```

### Ollama Model Download Fails

**Issue**: Network timeout or slow download

**Solution**: 
1. Check your internet connection
2. Try downloading again
3. Increase Docker memory limit in Docker Desktop settings

### PaddleOCR Installation Fails

**Issue**: Missing system dependencies

**Solution** (Linux):
```bash
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

**Solution** (macOS):
```bash
brew install opencv
```

### GPU Not Detected

**Issue**: CUDA/GPU not available

**Solution**: 
1. Install NVIDIA drivers and CUDA toolkit
2. Install GPU-enabled PyTorch:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

3. Or run in CPU mode (slower):
   - Edit `backend/.env` and set `USE_GPU=false`

### Frontend Build Errors

**Issue**: Node version mismatch

**Solution**: Ensure you're using Node.js 18 or higher:
```bash
node --version
```

Use [nvm](https://github.com/nvm-sh/nvm) to manage Node versions:
```bash
nvm install 18
nvm use 18
```

## Next Steps

After successful setup:

1. Read the [README.md](README.md) for project overview
2. Review the [API documentation](http://localhost:8000/docs)
3. Check the `.kiro/specs/labinsight/` directory for detailed requirements and design
4. Start implementing features following the task list in `.kiro/specs/labinsight/tasks.md`

## Getting Help

If you encounter issues not covered here:

1. Check the logs in Docker containers:
   ```bash
   docker-compose logs mongodb
   docker-compose logs redis
   docker-compose logs ollama
   ```

2. Check backend logs (structured JSON output)

3. Check frontend console in browser DevTools

4. Open an issue on the GitHub repository with:
   - Error message
   - Steps to reproduce
   - System information (OS, Python version, Node version)
