# インフラ設計（ローカル実行前提・初版）

## 実行方式
- Docker Compose で全コンポーネント起動
- Windows では WSL2 推奨
- GPU利用はオプション（NVIDIAドライバ + WSL2 + CUDA）。未検出時はCPU自動で稼働

## ポート割り当て（デフォルト）
- Frontend: 5173
- Backend(FastAPI): 8000
- OCR Service: 8080
- n8n: 5678
- PostgreSQL: 5432
- Ollama: 11434

## 環境変数
- `.env.example` をルートに配置（パスワード/モデル名など）
- モデル切替は `.env` で `OLLAMA_MODEL` を変更するだけ（初期は軽量モデル）


