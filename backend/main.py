"""hight-agent-ai バックエンドアプリケーション

FastAPIベースのREST APIサーバー
OCR、RAG、LLMを統合した問題解答システム
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, ask_problem, documents
from app.db import init_db, close_db
from app.utils.logger import setup_logger

# ロガー設定
logger = setup_logger()

# APIプレフィックス
API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時
    logger.info("Starting hight-agent-ai backend...")
    try:
        await init_db()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    # 終了時
    logger.info("Shutting down hight-agent-ai backend...")
    try:
        await close_db()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# FastAPIアプリケーション
app = FastAPI(
    title="hight-agent-ai Backend",
    description="単位取得特化型AIエージェント - バックエンドAPI",
    version="0.1.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(health.router, prefix=API_PREFIX, tags=["health"])
app.include_router(ask_problem.router, prefix=API_PREFIX, tags=["problem"])
app.include_router(documents.router, prefix=API_PREFIX, tags=["documents"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "hight-agent-ai backend running",
        "version": "0.1.0",
        "docs": "/docs"
    }

