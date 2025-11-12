/**
 * フロントエンド型定義
 */

// メッセージ型
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  image?: string; // Base64エンコード画像
  referencedDocs?: ReferencedDocument[];
  timestamp: Date;
  processingTimeMs?: number;
}

// 参照資料
export interface ReferencedDocument {
  document_id: number;
  filename: string;
  subject: string | null;
  chunk_content: string;
}

// 解答レスポンス
export interface AnswerResponse {
  answer: string;
  referenced_documents: ReferencedDocument[];
  processing_time_ms: number;
}

// 資料情報
export interface DocumentInfo {
  id: number;
  filename: string;
  subject: string | null;
  status: 'processing' | 'completed' | 'failed';
  created_at: string;
  chunk_count: number;
}

// 資料一覧レスポンス
export interface DocumentListResponse {
  documents: DocumentInfo[];
  total: number;
}

// ヘルスチェックレスポンス
export interface HealthResponse {
  status: string;
  services: {
    database: string;
    ollama: string;
    ocr: string;
  };
}

