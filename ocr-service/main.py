"""hight-agent-ai OCRサービス

Tesseract OCRを使用した画像テキスト抽出サービス
"""
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ocr_processor import OCRProcessor

app = FastAPI(
    title="hight-agent-ai OCR Service",
    description="画像からテキストを抽出するOCRサービス",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCRプロセッサのインスタンス
ocr_processor = OCRProcessor(lang="jpn+eng")


@app.post("/api/ocr")
async def extract_text(image: UploadFile = File(..., description="OCR処理する画像")):
    """画像からテキストを抽出

    Args:
        image: 画像ファイル

    Returns:
        抽出されたMarkdownテキストと処理時間
    """
    start_time = time.time()

    try:
        # 画像データを読み込み
        image_bytes = await image.read()

        # OCR処理
        markdown = ocr_processor.process_image(image_bytes)

        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "markdown": markdown,
            "processing_time_ms": processing_time_ms
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/health")
async def health_check():
    """ヘルスチェック

    OCRエンジンの動作確認を含む
    """
    ocr_ok = ocr_processor.health_check()

    return {
        "status": "ok" if ocr_ok else "error",
        "ocr_engine": "tesseract",
        "languages": "jpn+eng"
    }


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "hight-agent-ai OCR Service",
        "version": "0.1.0",
        "docs": "/docs"
    }

