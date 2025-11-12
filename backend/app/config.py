"""環境変数と設定管理"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # データベース
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:admin_password@localhost:5432/hight_ai"
    )
    
    # Ollama
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    
    # OCR Service
    ocr_url: str = os.getenv("OCR_URL", "http://localhost:8080")
    
    # Embedding
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "intfloat/multilingual-e5-large"
    )
    embedding_dimension: int = 1024
    
    # ファイルアップロード
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 100
    allowed_extensions: list[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    
    # RAG設定
    rag_top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # LLM設定
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# グローバル設定インスタンス
settings = Settings()

