from pydantic_settings import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Propos4l"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Diretórios
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    VECTOR_INDEX_PATH: Path = BASE_DIR / "data" / "proposals.index"
    
    # Configurações de upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # Configurações de processamento
    BATCH_SIZE: int = 10
    MIN_CONFIDENCE_SCORE: float = 0.7
    
    # Configurações do banco de dados
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "propos4l")
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    class Config:
        case_sensitive = True

settings = Settings()
