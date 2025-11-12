"""RAGサービス - 検索・プロンプト構築・解答生成"""
from typing import List, Optional, Tuple
import asyncpg
from ..models.schemas import ReferencedDocument
from ..config import settings
from .embedding_service import EmbeddingService
from .llm_service import LLMService
from ..db.repositories import ChunkRepository


class RAGService:
    """RAG（Retrieval-Augmented Generation）サービス"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        llm_service: LLMService
    ):
        self.embedding = embedding_service
        self.llm = llm_service

    async def search_relevant_chunks(
        self,
        conn: asyncpg.Connection,
        query_text: str,
        top_k: Optional[int] = None,
        subject_filter: Optional[str] = None
    ) -> List[dict]:
        """ベクトル検索で関連チャンクを取得

        Args:
            conn: データベース接続
            query_text: 検索クエリ
            top_k: 取得件数（デフォルト: settings.rag_top_k）
            subject_filter: 科目でフィルタ

        Returns:
            類似チャンクのリスト
        """
        top_k = top_k or settings.rag_top_k

        # クエリをベクトル化
        query_vector = await self.embedding.embed_query(query_text)

        # ベクトル検索
        chunk_repo = ChunkRepository(conn)
        chunks = await chunk_repo.vector_search(
            query_embedding=query_vector,
            top_k=top_k,
            subject_filter=subject_filter
        )

        return chunks

    def build_prompt(
        self,
        question: str,
        chunks: List[dict]
    ) -> str:
        """RAG用プロンプトを構築

        Args:
            question: 学生の質問
            chunks: 検索で取得したチャンク

        Returns:
            構築されたプロンプト
        """
        if not chunks:
            # RAGなしの場合
            return self._build_no_rag_prompt(question)

        # コンテキストを構築
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            filename = chunk.get("filename", "不明")
            subject = chunk.get("subject", "")
            content = chunk.get("content", "")
            similarity = chunk.get("similarity", 0)

            subject_str = f"（{subject}）" if subject else ""
            context_parts.append(
                f"## 資料{i}: {filename}{subject_str}\n"
                f"関連度: {similarity:.2f}\n\n"
                f"{content}\n"
            )

        context = "\n".join(context_parts)

        # プロンプト構築
        prompt = f"""以下の授業資料を参考に、学生の質問に丁寧に解答してください。

# 参考資料
{context}

# 学生の質問
{question}

# 解答
数式は必ずLaTeX記法を使用し、インライン数式は $...$ で、ブロック数式は $$...$$ で囲んでください。
ステップバイステップで丁寧に説明し、必要に応じて図や具体例を用いてください。
参考資料の内容を適切に引用しながら、理解しやすい解答を心がけてください。"""

        return prompt

    def _build_no_rag_prompt(self, question: str) -> str:
        """RAGなしのプロンプトを構築"""
        prompt = f"""以下の学生の質問に、あなたの知識を使って丁寧に解答してください。

# 学生の質問
{question}

# 解答
数式は必ずLaTeX記法を使用し、インライン数式は $...$ で、ブロック数式は $$...$$ で囲んでください。
ステップバイステップで丁寧に説明し、必要に応じて図や具体例を用いてください。"""

        return prompt

    async def generate_answer(
        self,
        conn: asyncpg.Connection,
        question: str,
        use_rag: bool = True,
        subject_filter: Optional[str] = None
    ) -> Tuple[str, List[ReferencedDocument]]:
        """解答を生成

        Args:
            conn: データベース接続
            question: 質問文
            use_rag: RAG検索を使用するか
            subject_filter: 科目フィルタ

        Returns:
            (解答テキスト, 参照資料リスト)
        """
        chunks = []
        referenced_docs = []

        # RAG検索
        if use_rag:
            chunks = await self.search_relevant_chunks(
                conn=conn,
                query_text=question,
                subject_filter=subject_filter
            )

            # 参照資料情報を構築
            for chunk in chunks:
                referenced_docs.append(
                    ReferencedDocument(
                        document_id=chunk.get("document_id", 0),
                        filename=chunk.get("filename", "不明"),
                        subject=chunk.get("subject"),
                        chunk_content=chunk.get("content", "")[:200] + "..."  # 最初の200文字
                    )
                )

        # プロンプト構築
        prompt = self.build_prompt(question, chunks)

        # LLMで解答生成
        system_message = """あなたは理系大学の学習支援AIアシスタントです。
数学・物理などの問題に対して、正確でわかりやすい解答を提供してください。
数式はLaTeX記法で記述し、論理的に段階を追って説明してください。"""

        answer = await self.llm.generate(
            prompt=prompt,
            system=system_message,
            temperature=settings.llm_temperature
        )

        return answer, referenced_docs

