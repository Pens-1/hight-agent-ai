-- hight-agent-ai データベース初期化スクリプト
-- pgvector拡張を使用したベクトル検索対応

-- pgvector拡張の有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- 資料メタデータテーブル
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    subject TEXT,                          -- LLMによる分類科目（例: "数学", "物理(力学)"）
    original_path TEXT,                    -- 元ファイルのパス（ローカル保存用）
    status TEXT NOT NULL DEFAULT 'processing', -- processing | completed | failed
    error_message TEXT,                    -- 失敗時のエラー内容
    file_size_bytes BIGINT,                -- ファイルサイズ
    mime_type TEXT,                        -- MIMEタイプ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 資料インデックス
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

-- RAG用チャンクテーブル
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,                 -- 分割されたテキスト本文
    chunk_index INTEGER NOT NULL,          -- チャンク順序
    embedding VECTOR(1024) NOT NULL,       -- multilingual-e5-large (1024次元)
    metadata JSONB,                        -- 追加情報（ページ番号など）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- チャンクインデックス
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON chunks(document_id, chunk_index);

-- ベクトル類似度検索用インデックス（HNSW）
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- 会話履歴テーブル
CREATE TABLE IF NOT EXISTS conversations (
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

CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- updated_at自動更新用トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

