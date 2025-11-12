# コーディング規約（初版）

## フロントエンド
- 言語: TypeScript
- Lint/Format: ESLint + Prettier
- 命名: PascalCase(コンポーネント), camelCase(関数/変数)
- ディレクトリ: components/hooks/services/types/styles

## バックエンド
- フレームワーク: FastAPI
- Lint/Format: Ruff + Black
- 型: pydantic v2
- 層: api/services/db/models/utils

## 共通
- 早期return、深いネストを避ける
- 例外の握りつぶし禁止
- テスト必須（新規/重要修正）


