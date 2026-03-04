"""Main FastAPI application entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from config import settings
from logging_config import setup_logging
from database import db_manager
from redis_client import redis_client
from routes import auth, reports, ner, trends
from utils.error_handling import (
    LabInsightError,
    labinsight_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
import logging

# Setup structured logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="LabInsight Health Intelligence Platform",
    description="AI-powered medical lab report analysis platform",
    version="1.0.0",
)

# Register exception handlers
app.add_exception_handler(LabInsightError, labinsight_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(ner.router)  # NER service endpoint
app.include_router(trends.router)  # Trends analysis endpoint

# Optional: Include example protected routes for demonstration
# Remove this in production
try:
    from routes import example_protected
    app.include_router(example_protected.router)
except ImportError:
    pass  # Example routes not available

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting LabInsight application", extra={
        "environment": settings.environment,
        "mongodb_url": settings.mongodb_url,
        "ollama_host": settings.ollama_host,
    })
    
    # Connect to MongoDB with retry logic
    try:
        await db_manager.connect()
        logger.info("MongoDB connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
    
    # Connect to Redis
    try:
        await redis_client.connect()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down LabInsight application")
    
    # Disconnect from MongoDB
    await db_manager.disconnect()
    
    # Disconnect from Redis
    await redis_client.disconnect()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LabInsight API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    # Check MongoDB health
    db_health = await db_manager.health_check()
    
    # Check Redis health
    redis_health = await redis_client.health_check()
    
    return {
        "status": "healthy" if (db_health["healthy"] and redis_health["healthy"]) else "degraded",
        "environment": settings.environment,
        "services": {
            "api": "operational",
            "database": "operational" if db_health["healthy"] else "error",
            "redis": "operational" if redis_health["healthy"] else "error",
            "ollama": "pending",
        },
        "database_info": db_health,
        "redis_info": redis_health
    }
