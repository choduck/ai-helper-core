import os
import secrets
from typing import List, Dict, Any, Optional, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 기본 API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Helper Core"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # CORS 설정
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 데이터베이스 설정
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "gpt_for_team")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_HOST')}:{values.get('MYSQL_PORT')}/{values.get('MYSQL_DB')}"
    
    # OpenAI API 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    
    # ChromaDB 설정
    CHROMA_DB_DIR: str = "chroma_db"
    CHROMA_DB_HOST: Optional[str] = None  # 클라이언트 모드에서 사용
    CHROMA_DB_PORT: Optional[int] = None  # 클라이언트 모드에서 사용
    
    # 문서 처리 설정
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # 음성 API 설정
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY", "")
    
    # JWT 설정 (백엔드와 통합)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 