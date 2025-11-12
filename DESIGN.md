# hight-agent-ai 詳細設計書

## 1. システム全体設計

### 1.1 アーキテクチャ概要
本システムは以下の6つのコンポーネントから構成されるマイクロサービスアーキテクチャ：

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (React App)                   │
│                   localhost:5173 (dev)                   │
└────────────┬─────────────────────────────┬──────────────┘
             │                             │
             │ HTTP                        │ HTTP (Webhook)
             ▼                             ▼
    ┌────────────────┐            ┌───────────────┐
    │  FastAPI       │            │     n8n       │
    │  (API Server)  │            │  (Workflow)   │
    │  :8000         │            │  :5678        │
    └────┬───────┬───┘            └───────┬───────┘
         │       │                        │
         │       └────────┐      ┌────────┘
         │                │      │
         │                ▼      ▼
         │         ┌──────────────────┐
         │         │     Ollama       │
         │         │   (LLM Service)  │
         │         │     :11434       │
         │         └──────────────────┘
         │                │
         │                │
         ▼                ▼
    ┌──────────────────────────────┐
    │  DeepSeek-OCR Service        │
    │  (FastAPI Wrapper)           │
    │         :8080                │
    └──────────────────────────────┘
         │                │
         │                │
         ▼                ▼
    ┌──────────────────────────────┐
    │   PostgreSQL + pgvector      │
    │         :5432                │
    └──────────────────────────────┘
```

### 1.2 通信フロー

#### 資料アップロードフロー（バックグラウンド処理）
```
1. User → React: ファイル選択
2. React → n8n: POST /webhook/upload_document (multipart)
3. n8n → DeepSeek-OCR: 画像をMarkdownに変換
4. n8n → Ollama: 科目分類のためのLLM推論
5. n8n → Embedding Model: テキストをベクトル化
6. n8n → PostgreSQL: メタデータ + チャンクを保存
7. n8n → React: Webhook完了通知（オプション）
```

#### 問題解答フロー（リアルタイム処理）
```
1. User → React: 問題画像アップロード + 送信
2. React → FastAPI: POST /ask_problem_image
3. FastAPI → DeepSeek-OCR: 画像をテキスト化
4. FastAPI → Embedding Model: 問題文をベクトル化
5. FastAPI → PostgreSQL: pgvectorで類似チャンク検索
6. FastAPI → Ollama: コンテキスト + 問題で解答生成
7. FastAPI → React: 解答（Markdown）を返却
8. React: Markdownレンダリング（数式対応）
```

---

## 2. ディレクトリ構造

```
hight-agent-ai/
├── README.md                    # プロジェクト全体の説明
├── 仕様書.md                    # 要件定義（既存）
├── DESIGN.md                    # 本設計書
├── docker-compose.yml           # 全サービスのオーケストレーション
├── .env.example                 # 環境変数のテンプレート
│
├── frontend/                    # React フロントエンド
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── ChatInterface.tsx      # メインチャット画面
│       │   ├── DocumentManager.tsx    # 資料管理画面
│       │   ├── ImageUploader.tsx      # 画像アップロード共通コンポーネント
│       │   ├── MarkdownRenderer.tsx   # 数式対応Markdownレンダラー
│       │   └── SettingsPanel.tsx      # RAG/Web検索トグル
│       ├── hooks/
│       │   ├── useChat.ts             # チャット状態管理
│       │   └── useDocuments.ts        # 資料管理状態
│       ├── services/
│       │   ├── api.ts                 # FastAPI通信
│       │   └── n8nApi.ts              # n8n Webhook通信
│       ├── types/
│       │   └── index.ts               # TypeScript型定義
│       └── styles/
│           └── global.css             # TailwindCSS設定
│
├── backend/                     # FastAPI バックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── main.py                  # FastAPIアプリケーションエントリーポイント
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py            # 環境変数・設定
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py          # ヘルスチェック
│   │   │       ├── ask_problem.py     # 問題解答エンドポイント
│   │   │       └── documents.py       # 資料一覧取得（オプション）
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py         # DeepSeek-OCR呼び出し
│   │   │   ├── llm_service.py         # Ollama呼び出し
│   │   │   ├── embedding_service.py   # 埋め込みモデル
│   │   │   └── rag_service.py         # RAG検索・プロンプト構築
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py          # PostgreSQL接続
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── document_repo.py   # documentsテーブル操作
│   │   │       └── chunk_repo.py      # chunksテーブル操作
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Pydanticモデル
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py              # ロギング設定
│   └── tests/
│       ├── __init__.py
│       └── test_api.py
│
├── ocr-service/                 # DeepSeek-OCR サービス
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # FastAPIアプリケーション
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── ocr.py             # POST /ocr エンドポイント
│   │   └── services/
│   │       └── deepseek_ocr.py        # DeepSeek-OCRラッパー
│   └── tests/
│       └── test_ocr.py
│
├── n8n/                         # n8n ワークフロー定義
│   ├── workflows/
│   │   └── document_upload.json       # 資料アップロード処理ワークフロー
│   └── README.md                      # n8nセットアップ手順
│
├── database/                    # PostgreSQL 初期化
│   ├── init.sql                 # DB・テーブル作成スクリプト
│   └── Dockerfile               # PostgreSQL + pgvector
│
└── scripts/                     # ユーティリティスクリプト
    ├── setup_ollama.sh          # Ollama初期セットアップ（モデルダウンロード）
    ├── test_all_services.sh     # 全サービスのヘルスチェック
    └── clean_db.sh              # DB初期化スクリプト
```

---

## 3. データベース設計

### 3.1 スキーマ定義

```sql
-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- 資料メタデータテーブル
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    subject TEXT,                          -- LLMによる分類科目
    original_path TEXT,                     -- 元ファイルのパス（ローカル保存用）
    status TEXT NOT NULL DEFAULT 'processing', -- processing | completed | failed
    error_message TEXT,                     -- 失敗時のエラー内容
    file_size_bytes BIGINT,                -- ファイルサイズ
    mime_type TEXT,                        -- MIMEタイプ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 資料インデックス
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_subject ON documents(subject);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- RAG用チャンクテーブル
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,                 -- 分割されたテキスト本文
    chunk_index INTEGER NOT NULL,          -- チャンク順序
    embedding VECTOR(1024) NOT NULL,       -- multilingual-e5-large (1024次元)
    metadata JSONB,                        -- 追加情報（ページ番号など）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- チャンクインデックス
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_chunk_index ON chunks(document_id, chunk_index);

-- ベクトル類似度検索用インデックス（HNSW）
CREATE INDEX idx_chunks_embedding ON chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 会話履歴テーブル（オプション：将来的な拡張）
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    question_image_path TEXT,              -- 問題画像のパス
    answer TEXT NOT NULL,
    used_rag BOOLEAN DEFAULT TRUE,
    used_web_search BOOLEAN DEFAULT FALSE,
    referenced_chunks INTEGER[],           -- 参照したchunk IDの配列
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

### 3.2 データフロー

**資料登録時**
```
documents テーブル
  ↓ (1件挿入: status='processing')
  ↓
OCR + チャンク分割 + 埋め込み
  ↓
chunks テーブル
  ↓ (N件挿入: document_id外部キー)
  ↓
documents.status を 'completed' に更新
```

**RAG検索時**
```
1. 問題文をベクトル化
2. chunksテーブルでコサイン類似度検索
   SELECT content, document_id 
   FROM chunks 
   ORDER BY embedding <=> $1::vector 
   LIMIT 5;
3. documentsテーブルからメタデータ取得
4. プロンプト構築
```

---

## 4. コンポーネント詳細設計

### 4.1 FastAPI バックエンド

#### 4.1.1 主要エンドポイント

**POST /api/ask_problem_image**
```python
# リクエスト
{
    "image": File,                    # 問題画像（multipart）
    "use_rag": bool = True,          # RAG検索を使用するか
    "use_web_search": bool = False,  # Web検索を使用するか（将来実装）
    "session_id": str = None         # 会話セッションID（オプション）
}

# レスポンス
{
    "answer": str,                    # Markdown形式の解答
    "referenced_documents": [         # RAG使用時の参照資料
        {
            "document_id": int,
            "filename": str,
            "subject": str,
            "chunk_content": str      # 使用したチャンク内容の一部
        }
    ],
    "processing_time_ms": int
}
```

**POST /api/ask_problem_text**
```python
# リクエスト
{
    "question": str,                  # テキスト形式の質問
    "use_rag": bool = True,
    "use_web_search": bool = False,
    "session_id": str = None
}

# レスポンス
# ask_problem_imageと同じ
```

**GET /api/documents**
```python
# リクエスト（クエリパラメータ）
{
    "status": str = None,             # フィルタ: processing | completed | failed
    "subject": str = None,            # フィルタ: 科目名
    "limit": int = 50,
    "offset": int = 0
}

# レスポンス
{
    "documents": [
        {
            "id": int,
            "filename": str,
            "subject": str,
            "status": str,
            "created_at": str,
            "chunk_count": int        # 紐づくチャンク数
        }
    ],
    "total": int
}
```

**DELETE /api/documents/{document_id}**
```python
# レスポンス
{
    "success": bool,
    "message": str
}
```

**GET /api/health**
```python
# レスポンス
{
    "status": "ok",
    "services": {
        "database": "ok" | "error",
        "ollama": "ok" | "error",
        "ocr": "ok" | "error"
    }
}
```

#### 4.1.2 サービス層設計

**RAGService (`app/services/rag_service.py`)**
```python
class RAGService:
    def __init__(self, db_conn, embedding_service, llm_service):
        self.db = db_conn
        self.embedding = embedding_service
        self.llm = llm_service
    
    async def search_relevant_chunks(
        self, 
        query_text: str, 
        top_k: int = 5,
        subject_filter: str = None
    ) -> List[Chunk]:
        """ベクトル検索で関連チャンクを取得"""
        query_vector = await self.embedding.embed_text(query_text)
        return await self.db.chunks.vector_search(
            query_vector, 
            top_k, 
            subject_filter
        )
    
    async def build_prompt(
        self, 
        question: str, 
        chunks: List[Chunk]
    ) -> str:
        """プロンプト構築"""
        context = "\n\n".join([
            f"[資料: {c.document.filename} ({c.document.subject})]\n{c.content}"
            for c in chunks
        ])
        
        return f"""以下の授業資料を参考に、学生の質問に丁寧に解答してください。

# 参考資料
{context}

# 学生の質問
{question}

# 解答
数式はLaTeX記法（$$...$$）で記述してください。ステップバイステップで説明してください。
"""
    
    async def generate_answer(
        self, 
        question: str, 
        use_rag: bool = True
    ) -> AnswerResult:
        """解答生成のメイン処理"""
        chunks = []
        if use_rag:
            chunks = await self.search_relevant_chunks(question)
        
        prompt = await self.build_prompt(question, chunks) if chunks else question
        answer = await self.llm.generate(prompt)
        
        return AnswerResult(
            answer=answer,
            referenced_chunks=chunks
        )
```

**EmbeddingService (`app/services/embedding_service.py`)**
```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        self.model = SentenceTransformer(model_name)
    
    async def embed_text(self, text: str) -> List[float]:
        """テキストをベクトル化（非同期対応）"""
        # multilingual-e5では、検索クエリには"query: "プレフィックスを付ける
        prefixed = f"query: {text}"
        embedding = self.model.encode(prefixed, normalize_embeddings=True)
        return embedding.tolist()
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数ドキュメントをバッチでベクトル化"""
        # ドキュメントには"passage: "プレフィックスを付ける
        prefixed = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(prefixed, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
```

**LLMService (`app/services/llm_service.py`)**
```python
import aiohttp

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "qwen3:30b-instruct"  # 設定から読み込み
    
    async def generate(
        self, 
        prompt: str, 
        system: str = None,
        temperature: float = 0.7
    ) -> str:
        """Ollamaで文章生成"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "temperature": temperature,
                    "stream": False
                }
            ) as response:
                result = await response.json()
                return result["response"]
    
    async def classify_subject(self, text: str) -> str:
        """資料の科目分類"""
        prompt = f"""以下の授業資料の内容を分析し、科目を1つ選んでください。

資料内容:
{text[:2000]}  # 最初の2000文字のみ

科目リスト: 数学, 物理(力学), 物理(電磁気), 物理(熱力学), 物理(量子力学), 化学, 生物学, その他

回答は科目名のみを出力してください。"""
        
        return (await self.generate(prompt)).strip()
```

**OCRService (`app/services/ocr_service.py`)**
```python
import aiohttp

class DeepSeekOCRService:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    async def extract_text(self, image_bytes: bytes) -> str:
        """画像からMarkdown形式でテキスト抽出"""
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field('image', image_bytes, filename='image.png', content_type='image/png')
            
            async with session.post(
                f"{self.base_url}/api/ocr",
                data=form
            ) as response:
                result = await response.json()
                return result["markdown"]
```

### 4.2 OCR Service

#### 4.2.1 エンドポイント

**POST /api/ocr**
```python
# リクエスト
{
    "image": File  # 画像ファイル（multipart）
}

# レスポンス
{
    "markdown": str,              # 抽出されたMarkdownテキスト
    "processing_time_ms": int
}
```

#### 4.2.2 実装例（`ocr-service/main.py`）

```python
from fastapi import FastAPI, File, UploadFile
from deepseek_ocr import DeepSeekOCR  # 仮想のライブラリ
import time

app = FastAPI()
ocr_model = DeepSeekOCR()  # モデル初期化

@app.post("/api/ocr")
async def extract_text(image: UploadFile = File(...)):
    start = time.time()
    
    image_bytes = await image.read()
    markdown = ocr_model.process(image_bytes)
    
    return {
        "markdown": markdown,
        "processing_time_ms": int((time.time() - start) * 1000)
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 4.3 n8n ワークフロー設計

#### 4.3.1 ワークフロー: 資料アップロード処理

**ノード構成**
```
1. Webhook (POST /webhook/upload_document)
   ↓
2. Function: ファイル情報取得
   ↓
3. HTTP Request: OCR Service (画像→Markdown)
   ↓
4. Function: チャンク分割（1000文字/チャンク、200文字オーバーラップ）
   ↓
5. HTTP Request: Ollama (科目分類)
   ↓
6. PostgreSQL: documentsテーブルにINSERT
   ↓
7. Loop: 各チャンクについて
   ├─ HTTP Request: Embedding Service (FastAPIに追加実装)
   └─ PostgreSQL: chunksテーブルにINSERT
   ↓
8. PostgreSQL: documentsのstatusを'completed'に更新
   ↓
9. Response: 完了メッセージ
```

**主要ノード設定**

*Webhook Node*
```json
{
  "method": "POST",
  "path": "/webhook/upload_document",
  "responseMode": "lastNode",
  "options": {
    "rawBody": false
  }
}
```

*Function Node: チャンク分割*
```javascript
// n8nのFunction Node内で実行
const text = items[0].json.markdown;
const chunkSize = 1000;
const overlap = 200;
const chunks = [];

for (let i = 0; i < text.length; i += (chunkSize - overlap)) {
  chunks.push({
    content: text.slice(i, i + chunkSize),
    chunk_index: chunks.length
  });
}

return chunks.map(chunk => ({ json: chunk }));
```

### 4.4 フロントエンド設計

#### 4.4.1 主要コンポーネント

**ChatInterface.tsx**
```typescript
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  image?: string;  // Base64エンコード画像
  referencedDocs?: ReferencedDocument[];
  timestamp: Date;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [useRAG, setUseRAG] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleImageUpload = async (file: File) => {
    // 画像をプレビュー表示
    // FastAPIにPOST
    // レスポンスを新しいメッセージとして追加
  };
  
  return (
    <div className="flex flex-col h-screen">
      <Header />
      <SettingsPanel useRAG={useRAG} setUseRAG={setUseRAG} />
      <MessageList messages={messages} />
      <InputArea 
        onSendText={handleTextSend}
        onSendImage={handleImageUpload}
      />
    </div>
  );
};
```

**DocumentManager.tsx**
```typescript
interface Document {
  id: number;
  filename: string;
  subject: string;
  status: 'processing' | 'completed' | 'failed';
  created_at: string;
  chunk_count: number;
}

const DocumentManager: React.FC = () => {
  const { documents, loading, error } = useDocuments();
  
  const handleUpload = async (file: File) => {
    // n8n Webhookに送信
    const formData = new FormData();
    formData.append('file', file);
    await axios.post('http://localhost:5678/webhook/upload_document', formData);
  };
  
  const handleDelete = async (id: number) => {
    await axios.delete(`http://localhost:8000/api/documents/${id}`);
  };
  
  return (
    <div>
      <FileUploader onUpload={handleUpload} />
      <DocumentTable 
        documents={documents} 
        onDelete={handleDelete}
      />
    </div>
  );
};
```

**MarkdownRenderer.tsx**
```typescript
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const MarkdownRenderer: React.FC<{ content: string }> = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={{
        code: ({ node, inline, className, children, ...props }) => {
          // コードブロックのカスタムレンダリング
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
```

---

## 5. 環境構築

### 5.1 Docker Compose構成

```yaml
version: '3.8'

services:
  # PostgreSQL + pgvector
  postgres:
    build: ./database
    container_name: hight-ai-db
    environment:
      POSTGRES_DB: hight_ai
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Ollama
  ollama:
    image: ollama/ollama:latest
    container_name: hight-ai-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]  # GPU使用時

  # OCR Service
  ocr-service:
    build: ./ocr-service
    container_name: hight-ai-ocr
    ports:
      - "8080:8080"
    environment:
      - MODEL_PATH=/models
    volumes:
      - ./models:/models
    depends_on:
      - postgres

  # FastAPI Backend
  backend:
    build: ./backend
    container_name: hight-ai-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://admin:${DB_PASSWORD}@postgres:5432/hight_ai
      - OLLAMA_URL=http://ollama:11434
      - OCR_URL=http://ocr-service:8080
    volumes:
      - ./backend:/app
      - upload_files:/app/uploads
    depends_on:
      - postgres
      - ollama
      - ocr-service
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # n8n
  n8n:
    image: n8nio/n8n:latest
    container_name: hight-ai-n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/workflows:/home/node/.n8n/workflows
    depends_on:
      - postgres
      - ollama
      - ocr-service

  # Frontend (開発環境)
  frontend:
    build: ./frontend
    container_name: hight-ai-frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_N8N_WEBHOOK_URL=http://localhost:5678/webhook/upload_document
    command: npm run dev

volumes:
  postgres_data:
  ollama_data:
  n8n_data:
  upload_files:
```

### 5.2 環境変数（.env）

```bash
# Database
DB_PASSWORD=your_secure_password

# n8n
N8N_PASSWORD=your_n8n_password

# Ollama
OLLAMA_MODEL=qwen3:30b-instruct

# Embedding
EMBEDDING_MODEL=intfloat/multilingual-e5-large

# OCR
OCR_MODEL_PATH=/path/to/deepseek-ocr
```

---

## 6. セットアップ手順

### 6.1 初回セットアップ

```bash
# 1. リポジトリクローン
git clone https://github.com/your-org/hight-agent-ai.git
cd hight-agent-ai

# 2. 環境変数設定
cp .env.example .env
# .envを編集

# 3. Dockerコンテナ起動
docker-compose up -d

# 4. Ollamaモデルダウンロード
docker exec -it hight-ai-ollama ollama pull qwen3:30b-instruct

# 5. 埋め込みモデルダウンロード（backendコンテナ内で実行）
docker exec -it hight-ai-backend python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"

# 6. n8nワークフローインポート
# ブラウザで http://localhost:5678 にアクセス
# n8n/workflows/document_upload.json をインポート

# 7. フロントエンドアクセス
# http://localhost:5173
```

### 6.2 開発環境セットアップ（ローカル）

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 7. 実装の優先順位

### Phase 1: MVP（最小構成）
1. ✅ データベース設計・セットアップ
2. ✅ FastAPI基本構造 + ヘルスチェック
3. ✅ OCR Service基本実装
4. ✅ Ollama連携実装
5. ✅ 埋め込みサービス実装
6. ✅ RAG検索機能実装
7. ✅ POST /ask_problem_image 実装
8. ✅ React基本UI（チャット画面）
9. ✅ 画像アップロード→解答表示のE2Eテスト

### Phase 2: 資料管理機能
1. ✅ n8nワークフロー構築（資料アップロード）
2. ✅ POST /webhook/upload_document 実装
3. ✅ 科目自動分類実装
4. ✅ チャンク分割・ベクトル化・DB登録
5. ✅ React資料管理画面
6. ✅ 資料一覧・削除機能

### Phase 3: 品質向上
1. ✅ エラーハンドリング強化
2. ✅ ロギング整備
3. ✅ UI/UX改善（ローディング表示、エラー表示）
4. ✅ Markdown/数式レンダリング最適化
5. ✅ レスポンス速度改善

### Phase 4: 拡張機能（オプション）
1. 🔲 Web検索機能（SearXNG連携）
2. 🔲 会話履歴機能
3. 🔲 複数モデル切り替え
4. 🔲 ユーザー設定保存
5. 🔲 エクスポート機能（PDF/Markdown）

---

## 8. テスト戦略

### 8.1 単体テスト
- Backend: pytest + pytest-asyncio
- Frontend: Vitest + React Testing Library

### 8.2 統合テスト
- API E2Eテスト: Postman/pytest-httpx
- データベーステスト: テスト用DBでマイグレーション確認

### 8.3 パフォーマンステスト
- RAG検索速度: 目標 < 500ms
- LLM推論速度: 目標 < 10秒（Qwen3-30B）
- OCR処理速度: 目標 < 2秒

---

## 9. セキュリティ考慮事項

1. **ファイルアップロード制限**
   - ファイルサイズ上限: 10MB
   - 許可する拡張子: .pdf, .png, .jpg, .jpeg

2. **SQL インジェクション対策**
   - パラメータ化クエリ使用（psycopg2/asyncpg）

3. **XSS対策**
   - React標準のエスケープ機能
   - react-markdownの安全な設定

4. **CORS設定**
   - 開発環境: 全て許可
   - 本番環境: フロントエンドのオリジンのみ許可

---

## 10. 今後の課題

1. **スケーラビリティ**
   - 大量の資料登録時のベクトル検索速度
   - タスクキュー導入（Celery/Redis）

2. **モデル最適化**
   - 量子化モデルの検討（GGUF形式）
   - GPU/CPU自動切り替え

3. **ユーザビリティ**
   - オンボーディングチュートリアル
   - サンプル資料の提供

4. **監視・運用**
   - Prometheusでメトリクス収集
   - Grafanaでダッシュボード構築

