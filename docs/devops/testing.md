# テスト戦略（初版）

## 単体テスト
- Backend: pytest + pytest-asyncio
- Frontend: Vitest + React Testing Library
- OCR Service: FastAPI TestClient

## 結合テスト
- API E2E（問題画像→解答）
- DB操作（テストDB）

## パフォーマンス
- RAG検索（< 500ms）
- OCR（< 2s）
- 生成（< 10s）


