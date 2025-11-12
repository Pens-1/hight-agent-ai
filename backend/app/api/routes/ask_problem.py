"""問題解答エンドポイント"""
import time
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ...models.schemas import AskTextRequest, AnswerResponse
from ...services import OCRService, LLMService, EmbeddingService, RAGService
from ...db import get_db_connection
from ...db.repositories import ConversationRepository
from ...utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()

# サービスインスタンス（シングルトン的に使用）
_ocr_service: Optional[OCRService] = None
_llm_service: Optional[LLMService] = None
_embedding_service: Optional[EmbeddingService] = None
_rag_service: Optional[RAGService] = None


def get_services():
    """サービスインスタンスを取得（遅延初期化）"""
    global _ocr_service, _llm_service, _embedding_service, _rag_service
    
    if _ocr_service is None:
        _ocr_service = OCRService()
    if _llm_service is None:
        _llm_service = LLMService()
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    if _rag_service is None:
        _rag_service = RAGService(_embedding_service, _llm_service)
    
    return _ocr_service, _llm_service, _embedding_service, _rag_service


@router.post("/ask_problem_image", response_model=AnswerResponse)
async def ask_problem_image(
    image: UploadFile = File(..., description="問題画像"),
    use_rag: bool = Form(True, description="RAG検索を使用するか"),
    use_web_search: bool = Form(False, description="Web検索を使用するか"),
    session_id: Optional[str] = Form(None, description="会話セッションID")
):
    """画像による質問を受け付け、解答を返す

    Args:
        image: 問題画像ファイル
        use_rag: RAG検索を使用するか
        use_web_search: Web検索を使用するか（未実装）
        session_id: 会話セッションID

    Returns:
        解答レスポンス
    """
    start_time = time.time()
    
    try:
        # サービス取得
        ocr_service, _, _, rag_service = get_services()
        
        # セッションIDがない場合は生成
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 画像を読み込み
        image_bytes = await image.read()
        logger.info(f"Received image: {image.filename}, size: {len(image_bytes)} bytes")
        
        # OCRでテキスト化
        logger.info("Starting OCR...")
        question_text = await ocr_service.extract_text(image_bytes)
        logger.info(f"OCR completed: {len(question_text)} chars extracted")
        
        # RAG + LLMで解答生成
        logger.info(f"Generating answer (use_rag={use_rag})...")
        async with get_db_connection() as conn:
            answer, referenced_docs = await rag_service.generate_answer(
                conn=conn,
                question=question_text,
                use_rag=use_rag
            )
            
            # 会話履歴を保存
            conv_repo = ConversationRepository(conn)
            await conv_repo.create(
                session_id=session_id,
                question=question_text,
                answer=answer,
                used_rag=use_rag,
                used_web_search=use_web_search,
                referenced_chunks=[doc.document_id for doc in referenced_docs]
            )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Answer generated in {processing_time_ms}ms")
        
        return AnswerResponse(
            answer=answer,
            referenced_documents=referenced_docs,
            processing_time_ms=processing_time_ms
        )
        
    except ValueError as e:
        logger.error(f"ValueError in ask_problem_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in ask_problem_image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ask_problem_text", response_model=AnswerResponse)
async def ask_problem_text(req: AskTextRequest):
    """テキストによる質問を受け付け、解答を返す

    Args:
        req: テキスト質問リクエスト

    Returns:
        解答レスポンス
    """
    start_time = time.time()
    
    try:
        # サービス取得
        _, _, _, rag_service = get_services()
        
        # セッションIDがない場合は生成
        session_id = req.session_id or str(uuid.uuid4())
        
        logger.info(f"Received text question: {req.question[:100]}...")
        
        # RAG + LLMで解答生成
        logger.info(f"Generating answer (use_rag={req.use_rag})...")
        async with get_db_connection() as conn:
            answer, referenced_docs = await rag_service.generate_answer(
                conn=conn,
                question=req.question,
                use_rag=req.use_rag
            )
            
            # 会話履歴を保存
            conv_repo = ConversationRepository(conn)
            await conv_repo.create(
                session_id=session_id,
                question=req.question,
                answer=answer,
                used_rag=req.use_rag,
                used_web_search=req.use_web_search,
                referenced_chunks=[doc.document_id for doc in referenced_docs]
            )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Answer generated in {processing_time_ms}ms")
        
        return AnswerResponse(
            answer=answer,
            referenced_documents=referenced_docs,
            processing_time_ms=processing_time_ms
        )
        
    except ValueError as e:
        logger.error(f"ValueError in ask_problem_text: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in ask_problem_text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

