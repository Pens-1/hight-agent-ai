"""Documentテーブル操作"""
from typing import Optional, List
from datetime import datetime
import asyncpg


class DocumentRepository:
    """資料メタデータリポジトリ"""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def create(
        self,
        filename: str,
        subject: Optional[str] = None,
        original_path: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        mime_type: Optional[str] = None,
        status: str = "processing"
    ) -> int:
        """資料を新規作成

        Returns:
            作成された資料のID
        """
        row = await self.conn.fetchrow(
            """
            INSERT INTO documents 
            (filename, subject, original_path, file_size_bytes, mime_type, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            filename, subject, original_path, file_size_bytes, mime_type, status
        )
        return row["id"]

    async def get_by_id(self, document_id: int) -> Optional[dict]:
        """IDで資料を取得"""
        row = await self.conn.fetchrow(
            "SELECT * FROM documents WHERE id = $1",
            document_id
        )
        return dict(row) if row else None

    async def list_documents(
        self,
        status: Optional[str] = None,
        subject: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """資料一覧を取得"""
        query = """
            SELECT 
                d.*,
                COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN chunks c ON d.id = c.document_id
            WHERE 1=1
        """
        params = []
        param_index = 1

        if status:
            query += f" AND d.status = ${param_index}"
            params.append(status)
            param_index += 1

        if subject:
            query += f" AND d.subject = ${param_index}"
            params.append(subject)
            param_index += 1

        query += f"""
            GROUP BY d.id
            ORDER BY d.created_at DESC
            LIMIT ${param_index} OFFSET ${param_index + 1}
        """
        params.extend([limit, offset])

        rows = await self.conn.fetch(query, *params)
        return [dict(row) for row in rows]

    async def count_documents(
        self,
        status: Optional[str] = None,
        subject: Optional[str] = None
    ) -> int:
        """資料数を取得"""
        query = "SELECT COUNT(*) as count FROM documents WHERE 1=1"
        params = []
        param_index = 1

        if status:
            query += f" AND status = ${param_index}"
            params.append(status)
            param_index += 1

        if subject:
            query += f" AND subject = ${param_index}"
            params.append(subject)

        row = await self.conn.fetchrow(query, *params)
        return row["count"]

    async def update_status(
        self,
        document_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """資料のステータスを更新"""
        result = await self.conn.execute(
            """
            UPDATE documents 
            SET status = $1, error_message = $2, updated_at = CURRENT_TIMESTAMP
            WHERE id = $3
            """,
            status, error_message, document_id
        )
        return result == "UPDATE 1"

    async def update_subject(self, document_id: int, subject: str) -> bool:
        """資料の科目を更新"""
        result = await self.conn.execute(
            """
            UPDATE documents 
            SET subject = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
            """,
            subject, document_id
        )
        return result == "UPDATE 1"

    async def delete(self, document_id: int) -> bool:
        """資料を削除（関連チャンクも自動削除）"""
        result = await self.conn.execute(
            "DELETE FROM documents WHERE id = $1",
            document_id
        )
        return result == "DELETE 1"

