"""Pydanticデータモデル定義"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# リクエストモデル
class AskTextRequest(BaseModel):
    """テキスト質問リクエスト"""
    question: str = Field(..., min_length=1, description="質問テキスト")
    use_rag: bool = Field(True, description="RAG検索を使用するか")
    use_web_search: bool = Field(False, description="Web検索を使用するか")
    session_id: Optional[str] = Field(None, description="会話セッションID")


class AskImageRequest(BaseModel):
    """画像質問リクエスト（multipart用）"""
    use_rag: bool = Field(True, description="RAG検索を使用するか")
    use_web_search: bool = Field(False, description="Web検索を使用するか")
    session_id: Optional[str] = Field(None, description="会話セッションID")


# レスポンスモデル
class ReferencedDocument(BaseModel):
    """参照資料情報"""
    document_id: int
    filename: str
    subject: Optional[str]
    chunk_content: str = Field(..., description="使用したチャンク内容の一部")


class AnswerResponse(BaseModel):
    """解答レスポンス"""
    answer: str = Field(..., description="Markdown形式の解答")
    referenced_documents: list[ReferencedDocument] = Field(
        default_factory=list,
        description="RAG使用時の参照資料"
    )
    processing_time_ms: int = Field(..., description="処理時間（ミリ秒）")


# ドキュメント関連
class DocumentInfo(BaseModel):
    """資料情報"""
    id: int
    filename: str
    subject: Optional[str]
    status: str
    created_at: datetime
    chunk_count: int = 0


class DocumentListResponse(BaseModel):
    """資料一覧レスポンス"""
    documents: list[DocumentInfo]
    total: int


class DocumentDeleteResponse(BaseModel):
    """資料削除レスポンス"""
    success: bool
    message: str


# ヘルスチェック
class ServiceStatus(BaseModel):
    """サービス状態"""
    database: str
    ollama: str
    ocr: str


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    services: ServiceStatus


# データベースモデル
class Document(BaseModel):
    """資料メタデータ"""
    id: int
    filename: str
    subject: Optional[str]
    original_path: Optional[str]
    status: str
    error_message: Optional[str]
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    created_at: datetime
    updated_at: datetime


class Chunk(BaseModel):
    """テキストチャンク"""
    id: int
    document_id: int
    content: str
    chunk_index: int
    metadata: Optional[dict]
    created_at: datetime
    
    # JOIN時に追加される情報
    document: Optional[Document] = None
    similarity: Optional[float] = None


class Conversation(BaseModel):
    """会話履歴"""
    id: int
    session_id: str
    question: str
    question_image_path: Optional[str]
    answer: str
    used_rag: bool
    used_web_search: bool
    referenced_chunks: Optional[list[int]]
    created_at: datetime

