# API 設計（FastAPI / n8n）初版

ベースURLはローカル実行を想定。
- FastAPI: `http://localhost:8000/api`
- n8n Webhook: `http://localhost:5678/webhook`

---

## POST /api/ask_problem_image
- 概要: 画像による質問を受け付け、解答を返す
- リクエスト: multipart/form-data
  - image: File (必須)
  - use_rag: boolean (デフォルト: true)
  - use_web_search: boolean (デフォルト: false)
  - session_id: string (任意)
  - 制限: 100MB まで
- レスポンス: application/json
```json
{
  "answer": "Markdown string",
  "referenced_documents": [
    {
      "document_id": 1,
      "filename": "calc.pdf",
      "subject": "数学",
      "chunk_content": "..."
    }
  ],
  "processing_time_ms": 3210
}
```

## POST /api/ask_problem_text
- 概要: テキスト質問に対する解答を返す
- リクエスト: application/json
```json
{
  "question": "テイラー展開の定義を教えて",
  "use_rag": true,
  "use_web_search": false,
  "session_id": "abc-123"
}
```
- レスポンス: ask_problem_image と同様

## GET /api/documents
- 概要: 登録済み資料の一覧取得
- クエリ:
  - status: processing|completed|failed
  - subject: string
  - limit: number (default 50)
  - offset: number (default 0)
- レスポンス:
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "calc.pdf",
      "subject": "数学",
      "status": "completed",
      "created_at": "2025-01-01T12:34:56Z",
      "chunk_count": 42
    }
  ],
  "total": 1
}
```

## DELETE /api/documents/{document_id}
- 概要: 資料と紐付くチャンクを削除
- レスポンス:
```json
{
  "success": true,
  "message": "deleted"
}
```

## GET /api/health
- 概要: 依存サービスのヘルスチェック
- レスポンス:
```json
{
  "status": "ok",
  "services": {
    "database": "ok",
    "ollama": "ok",
    "ocr": "ok"
  }
}
```

---

## POST /webhook/upload_document (n8n)
- 概要: 資料アップロード受付（非同期処理）
- リクエスト: multipart/form-data
  - file: File (必須)
  - 制限: 100MB まで
- レスポンス:
```json
{
  "accepted": true,
  "message": "processing started"
}
```

---

## 認証・認可（案）
- ローカル単体利用を前提に「認証なし」から開始
- 今後の拡張: Basic認証 or ローカルプロフィール（PIN）


