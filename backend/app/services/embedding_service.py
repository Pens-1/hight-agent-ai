"""埋め込みサービス - Sentence Transformers"""
import asyncio
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from ..config import settings


class EmbeddingService:
    """埋め込みサービス（multilingual-e5-large）"""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self):
        """モデルを遅延ロード"""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

    async def embed_query(self, text: str) -> List[float]:
        """検索クエリをベクトル化

        multilingual-e5では、検索クエリには"query: "プレフィックスを付ける

        Args:
            text: クエリテキスト

        Returns:
            1024次元のベクトル
        """
        self._load_model()
        
        # 検索クエリには"query: "プレフィックスを付ける
        prefixed = f"query: {text}"
        
        # 非同期実行（CPUバウンドな処理をブロックしないため）
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self._model.encode(
                prefixed,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        )
        
        return embedding.tolist()

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数ドキュメントをバッチでベクトル化

        multilingual-e5では、ドキュメントには"passage: "プレフィックスを付ける

        Args:
            texts: ドキュメントテキストのリスト

        Returns:
            1024次元のベクトルのリスト
        """
        self._load_model()
        
        # ドキュメントには"passage: "プレフィックスを付ける
        prefixed = [f"passage: {text}" for text in texts]
        
        # 非同期実行
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self._model.encode(
                prefixed,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=False
            )
        )
        
        return embeddings.tolist()

    async def embed_document(self, text: str) -> List[float]:
        """単一ドキュメントをベクトル化

        Args:
            text: ドキュメントテキスト

        Returns:
            1024次元のベクトル
        """
        result = await self.embed_documents([text])
        return result[0]

