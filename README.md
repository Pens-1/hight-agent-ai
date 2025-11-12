# hight-agent-ai

単位取得特化型AIエージェント - 理系大学生の学習を支援するローカル完結型AIシステム

## 概要

hight-agent-aiは、理系大学の学部初期課程の学生を対象に、数学・物理などの学習を支援するAIエージェントです。

### 主な特徴

- **ローカル完結**: すべての処理（LLM推論、OCR、データベース）がローカル環境で完結
- **RAG（Retrieval-Augmented Generation）**: アップロードした授業資料に基づいた精度の高い解答
- **OCR対応**: 手書きや印刷された問題の画像から自動テキスト化
- **自動分類**: アップロードした資料を科目別に自動分類
- **プライバシー保護**: データは外部に送信されず、すべてローカルに保存

## 技術スタック

### フロントエンド
- React + TypeScript + Vite
- TailwindCSS
- Zustand（状態管理）
- react-markdown + KaTeX（数式レンダリング）

### バックエンド
- Python 3.11 + FastAPI
- PostgreSQL + pgvector（ベクトル検索）
- Ollama（LLM: Qwen2.5）
- Tesseract OCR（画像テキスト抽出）
- Sentence Transformers（埋め込みモデル）

### インフラ
- Docker + Docker Compose
- n8n（ワークフロー自動化）

## 必要要件

- Docker & Docker Compose
- メモリ: 16GB以上推奨
- ストレージ: 20GB以上の空き容量
- （オプション）NVIDIA GPU（LLM推論の高速化）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/hight-agent-ai.git
cd hight-agent-ai
```

### 2. セットアップスクリプトの実行

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

このスクリプトは以下を実行します：
- `.env` ファイルの作成
- Dockerコンテナの起動（PostgreSQL, Ollama, OCR Service）
- Ollamaモデルのダウンロード

### 3. すべてのサービスを起動

```bash
docker-compose up -d
```

### 4. アクセス

- **フロントエンド**: http://localhost:5173
- **APIドキュメント**: http://localhost:8000/docs
- **n8n**: http://localhost:5678 (admin / n8n_admin_password)

## 使い方

### チャット機能

1. http://localhost:5173 にアクセス
2. 「チャット」タブで質問を入力またはフ画像をアップロード
3. RAG検索を有効にすると、アップロードした資料を参照して解答

### 資料管理

1. 「資料管理」タブに移動
2. PDFや画像ファイルをアップロード
3. n8nワークフローが自動的に：
   - OCRでテキスト化
   - LLMで科目分類
   - ベクトル化してデータベースに登録

## 開発

### バックエンドの開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### フロントエンドの開発

```bash
cd frontend
npm install
npm run dev
```

### テストの実行

```bash
cd backend
pytest
```

## プロジェクト構造

```
hight-agent-ai/
├── backend/           # FastAPIバックエンド
│   ├── app/
│   │   ├── api/      # APIルート
│   │   ├── services/ # ビジネスロジック
│   │   ├── db/       # データベース接続・リポジトリ
│   │   └── models/   # データモデル
│   └── tests/        # テストコード
├── frontend/         # Reactフロントエンド
│   └── src/
│       ├── components/ # UIコンポーネント
│       ├── services/   # API通信
│       ├── store/      # 状態管理
│       └── types/      # 型定義
├── ocr-service/      # OCRサービス
├── database/         # PostgreSQL初期化
├── n8n/              # n8nワークフロー定義
├── scripts/          # ユーティリティスクリプト
└── docs/             # 設計ドキュメント
```

## トラブルシューティング

### Ollamaモデルがダウンロードできない

```bash
docker exec -it hight-ai-ollama ollama pull qwen2.5:7b-instruct
```

### データベースをリセットしたい

```bash
chmod +x scripts/clean_db.sh
./scripts/clean_db.sh
```

### ポートが使用中

`.env` ファイルまたは `docker-compose.yml` でポート番号を変更してください。

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ブランチ戦略

- `main`: 安定版
- `feature/*`: 新機能開発
- `fix/*`: バグ修正
- `docs/*`: ドキュメント更新

## お問い合わせ

Issue または Discussion でお気軽にご質問ください。

