"""Application configuration management."""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "labinsight"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b-instruct"
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"
    max_file_size_mb: int = 10
    rate_limit_per_minute: int = 100
    
    # File Storage
    upload_dir: str = "./uploads"
    
    # AI Model Configuration
    use_gpu: bool = True
    ocr_language: str = "en"
    huggingface_cache_dir: Optional[str] = None  # Set to use custom cache directory
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Configure HuggingFace cache directory if specified
if settings.huggingface_cache_dir:
    os.environ["HF_HOME"] = settings.huggingface_cache_dir
    os.environ["TRANSFORMERS_CACHE"] = settings.huggingface_cache_dir
