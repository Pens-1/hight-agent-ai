from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="hight-agent-ai OCR Service")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.post("/api/ocr")
async def extract_text(image: UploadFile = File(...)):
	start = time.time()
	_ = await image.read()  # 実装時にOCRへ渡す
	# スケルトン: ダミーMarkdown
	markdown = "# OCR Placeholder\n\nこのテキストはダミーです。"
	return {
		"markdown": markdown,
		"processing_time_ms": int((time.time() - start) * 1000),
	}


@app.get("/health")
def health():
	return {"status": "ok"}


