"""PostgreSQL接続管理"""
import asyncpg
from typing import Optional
from ..config import settings


# グローバル接続プール
_pool: Optional[asyncpg.Pool] = None


async def init_db() -> asyncpg.Pool:
    """データベース接続プールを初期化"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
    return _pool


async def close_db():
    """データベース接続プールを閉じる"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_db_connection():
    """データベース接続を取得

    使用例:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM documents")
    """
    global _pool
    if _pool is None:
        await init_db()
    return _pool.acquire()

