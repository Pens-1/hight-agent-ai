# システムアーキテクチャ（初版）

## コンポーネント
- Frontend (React + Vite + TS)
- Backend (FastAPI)
- OCR Service (FastAPI/DeepSeek-OCR ラッパー)
- n8n (ワークフロー)
- PostgreSQL + pgvector
- Ollama (Qwen3)

## フロー概要
1) 資料アップロード（バックグラウンド）
- React → n8n(Webhook) → OCR → 分類 → 埋め込み → DB登録

2) 問題解答（リアルタイム）
- React → FastAPI → OCR → ベクトル検索 → LLM生成 → React

## 非同期連携
- n8nのWebhook起点で非同期実行
- DBの `documents.status` で進捗をUI表示


