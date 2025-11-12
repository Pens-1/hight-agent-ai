"""ヘルスチェックエンドポイント"""
from fastapi import APIRouter
from ...models.schemas import HealthResponse, ServiceStatus
from ...services import OCRService, LLMService
from ...db import get_db_connection
from ...config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """ヘルスチェック

    全サービスの稼働状態を確認
    """
    services = ServiceStatus(
        database="unknown",
        ollama="unknown",
        ocr="unknown"
    )

    # データベース接続チェック
    try:
        async with get_db_connection() as conn:
            await conn.fetchval("SELECT 1")
            services.database = "ok"
    except Exception:
        services.database = "error"

    # Ollamaチェック
    try:
        llm_service = LLMService()
        if await llm_service.health_check():
            services.ollama = "ok"
        else:
            services.ollama = "error"
    except Exception:
        services.ollama = "error"

    # OCRチェック
    try:
        ocr_service = OCRService()
        if await ocr_service.health_check():
            services.ocr = "ok"
        else:
            services.ocr = "error"
    except Exception:
        services.ocr = "error"

    # 全体のステータス
    all_ok = all([
        services.database == "ok",
        services.ollama == "ok",
        services.ocr == "ok"
    ])

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        services=services
    )

