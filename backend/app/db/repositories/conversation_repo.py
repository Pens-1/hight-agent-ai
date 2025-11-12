"""Conversationテーブル操作"""
from typing import Optional, List
import asyncpg


class ConversationRepository:
    """会話履歴リポジトリ"""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def create(
        self,
        session_id: str,
        question: str,
        answer: str,
        question_image_path: Optional[str] = None,
        used_rag: bool = True,
        used_web_search: bool = False,
        referenced_chunks: Optional[List[int]] = None
    ) -> int:
        """会話を記録

        Returns:
            作成された会話ID
        """
        row = await self.conn.fetchrow(
            """
            INSERT INTO conversations 
            (session_id, question, question_image_path, answer, used_rag, used_web_search, referenced_chunks)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            session_id,
            question,
            question_image_path,
            answer,
            used_rag,
            used_web_search,
            referenced_chunks or []
        )
        return row["id"]

    async def get_by_session_id(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """セッションIDで会話履歴を取得"""
        rows = await self.conn.fetch(
            """
            SELECT * FROM conversations
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            session_id, limit, offset
        )
        return [dict(row) for row in rows]

    async def get_by_id(self, conversation_id: int) -> Optional[dict]:
        """IDで会話を取得"""
        row = await self.conn.fetchrow(
            "SELECT * FROM conversations WHERE id = $1",
            conversation_id
        )
        return dict(row) if row else None

