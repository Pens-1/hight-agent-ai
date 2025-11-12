"""Chunkテーブル操作"""
from typing import List, Optional
import asyncpg


class ChunkRepository:
    """テキストチャンクリポジトリ"""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def create(
        self,
        document_id: int,
        content: str,
        chunk_index: int,
        embedding: List[float],
        metadata: Optional[dict] = None
    ) -> int:
        """チャンクを新規作成

        Args:
            document_id: 紐づく資料ID
            content: テキスト本文
            chunk_index: チャンク順序
            embedding: ベクトル（1024次元）
            metadata: 追加情報（ページ番号など）

        Returns:
            作成されたチャンクID
        """
        row = await self.conn.fetchrow(
            """
            INSERT INTO chunks 
            (document_id, content, chunk_index, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            document_id, content, chunk_index, embedding, metadata
        )
        return row["id"]

    async def create_batch(
        self,
        chunks: List[tuple[int, str, int, List[float], Optional[dict]]]
    ) -> List[int]:
        """複数チャンクを一括作成

        Args:
            chunks: (document_id, content, chunk_index, embedding, metadata)のリスト

        Returns:
            作成されたチャンクIDのリスト
        """
        rows = await self.conn.fetch(
            """
            INSERT INTO chunks 
            (document_id, content, chunk_index, embedding, metadata)
            SELECT * FROM UNNEST($1::int[], $2::text[], $3::int[], $4::vector[], $5::jsonb[])
            RETURNING id
            """,
            [c[0] for c in chunks],  # document_ids
            [c[1] for c in chunks],  # contents
            [c[2] for c in chunks],  # chunk_indexes
            [c[3] for c in chunks],  # embeddings
            [c[4] for c in chunks],  # metadata
        )
        return [row["id"] for row in rows]

    async def vector_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        subject_filter: Optional[str] = None
    ) -> List[dict]:
        """ベクトル類似度検索

        Args:
            query_embedding: クエリベクトル
            top_k: 取得件数
            subject_filter: 科目でフィルタ（オプション）

        Returns:
            類似チャンクのリスト（document情報付き）
        """
        query = """
            SELECT 
                c.*,
                d.filename,
                d.subject,
                1 - (c.embedding <=> $1::vector) as similarity
            FROM chunks c
            INNER JOIN documents d ON c.document_id = d.id
            WHERE d.status = 'completed'
        """
        params = [query_embedding]
        param_index = 2

        if subject_filter:
            query += f" AND d.subject = ${param_index}"
            params.append(subject_filter)
            param_index += 1

        query += f"""
            ORDER BY c.embedding <=> $1::vector
            LIMIT ${param_index}
        """
        params.append(top_k)

        rows = await self.conn.fetch(query, *params)
        return [dict(row) for row in rows]

    async def get_by_document_id(
        self,
        document_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """特定資料のチャンクを取得"""
        rows = await self.conn.fetch(
            """
            SELECT * FROM chunks
            WHERE document_id = $1
            ORDER BY chunk_index
            LIMIT $2 OFFSET $3
            """,
            document_id, limit, offset
        )
        return [dict(row) for row in rows]

    async def count_by_document_id(self, document_id: int) -> int:
        """特定資料のチャンク数を取得"""
        row = await self.conn.fetchrow(
            "SELECT COUNT(*) as count FROM chunks WHERE document_id = $1",
            document_id
        )
        return row["count"]

    async def delete_by_document_id(self, document_id: int) -> int:
        """特定資料のチャンクを全削除

        Returns:
            削除件数
        """
        result = await self.conn.execute(
            "DELETE FROM chunks WHERE document_id = $1",
            document_id
        )
        # "DELETE N" の形式で返るので、件数を抽出
        return int(result.split()[-1])

