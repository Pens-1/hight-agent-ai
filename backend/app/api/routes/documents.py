"""資料管理エンドポイント"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...models.schemas import (
    DocumentListResponse,
    DocumentInfo,
    DocumentDeleteResponse
)
from ...db import get_db_connection
from ...db.repositories import DocumentRepository
from ...utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    status: Optional[str] = Query(None, description="ステータスフィルタ"),
    subject: Optional[str] = Query(None, description="科目フィルタ"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット")
):
    """資料一覧を取得

    Args:
        status: ステータスフィルタ（processing/completed/failed）
        subject: 科目フィルタ
        limit: 取得件数
        offset: オフセット

    Returns:
        資料一覧
    """
    try:
        async with get_db_connection() as conn:
            doc_repo = DocumentRepository(conn)
            
            # 資料一覧取得
            documents = await doc_repo.list_documents(
                status=status,
                subject=subject,
                limit=limit,
                offset=offset
            )
            
            # 総件数取得
            total = await doc_repo.count_documents(
                status=status,
                subject=subject
            )
            
            # レスポンス構築
            doc_infos = [
                DocumentInfo(
                    id=doc["id"],
                    filename=doc["filename"],
                    subject=doc.get("subject"),
                    status=doc["status"],
                    created_at=doc["created_at"],
                    chunk_count=doc.get("chunk_count", 0)
                )
                for doc in documents
            ]
            
            return DocumentListResponse(
                documents=doc_infos,
                total=total
            )
            
    except Exception as e:
        logger.error(f"Error in list_documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: int):
    """資料を削除

    Args:
        document_id: 資料ID

    Returns:
        削除結果
    """
    try:
        async with get_db_connection() as conn:
            doc_repo = DocumentRepository(conn)
            
            # 資料の存在確認
            document = await doc_repo.get_by_id(document_id)
            if not document:
                raise HTTPException(
                    status_code=404,
                    detail=f"Document {document_id} not found"
                )
            
            # 削除実行（関連チャンクも自動削除される）
            success = await doc_repo.delete(document_id)
            
            if success:
                logger.info(f"Deleted document: {document_id}")
                return DocumentDeleteResponse(
                    success=True,
                    message=f"Document {document_id} deleted successfully"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to delete document"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

