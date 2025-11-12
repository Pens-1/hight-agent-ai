# アプリ機能要件（初版）

## 学習支援（問題解答）
- 画像アップロードでの質問（OCR → RAG → 解答生成）
- テキスト質問（RAGオン/オフ切替）
- Web検索併用（将来オプション）
- Markdown表示（数式はKaTeX）

## 資料管理
- PDF/画像アップロード（n8n Webhook 経由）
- 自動OCR → 自動科目分類 → チャンク化 → ベクトル登録
- 一覧表示・削除・ステータス確認（processing/completed/failed）

## システム
- ローカルDB（PostgreSQL + pgvector）
- LLM（Ollama/Qwen3）
- OCR（DeepSeek-OCR ラッパー）


