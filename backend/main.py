from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time

API_PREFIX = "/api"

app = FastAPI(title="hight-agent-ai Backend")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class AskTextRequest(BaseModel):
	question: str
	use_rag: bool = True
	use_web_search: bool = False
	session_id: str | None = None


@app.get(f"{API_PREFIX}/health")
def health():
	# 簡易版（本実装ではDB/OCR/LLMの疎通を追加）
	return {
		"status": "ok",
		"services": {
			"database": "unknown",
			"ollama": "unknown",
			"ocr": "unknown",
		},
	}


@app.post(f"{API_PREFIX}/ask_problem_text")
def ask_problem_text(req: AskTextRequest):
	start = time.time()
	# MVPスケルトン: エコー + ダミー
	answer = f"（暫定応答）質問: {req.question}\n\nRAG: {req.use_rag}, Web検索: {req.use_web_search}"
	return {
		"answer": answer,
		"referenced_documents": [],
		"processing_time_ms": int((time.time() - start) * 1000),
	}


@app.post(f"{API_PREFIX}/ask_problem_image")
async def ask_problem_image(
	image: UploadFile = File(...),
	use_rag: bool = Form(True),
	use_web_search: bool = Form(False),
	session_id: str | None = Form(None),
):
	start = time.time()
	_ = await image.read()  # 実装時にOCRへ渡す
	answer = f"（暫定応答）画像質問を受け付けました。RAG: {use_rag}, Web検索: {use_web_search}"
	return {
		"answer": answer,
		"referenced_documents": [],
		"processing_time_ms": int((time.time() - start) * 1000),
	}


@app.get("/")
def root():
	return {"message": "hight-agent-ai backend running"}


