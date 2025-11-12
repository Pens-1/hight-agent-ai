/**
 * FastAPI バックエンドとの通信
 */
import axios from 'axios';
import type { AnswerResponse, DocumentListResponse, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 120000, // 2分（LLM生成に時間がかかるため）
});

/**
 * テキスト質問を送信
 */
export async function askProblemText(
  question: string,
  useRAG: boolean = true,
  useWebSearch: boolean = false,
  sessionId?: string
): Promise<AnswerResponse> {
  const response = await apiClient.post<AnswerResponse>('/ask_problem_text', {
    question,
    use_rag: useRAG,
    use_web_search: useWebSearch,
    session_id: sessionId,
  });
  return response.data;
}

/**
 * 画像質問を送信
 */
export async function askProblemImage(
  imageFile: File,
  useRAG: boolean = true,
  useWebSearch: boolean = false,
  sessionId?: string
): Promise<AnswerResponse> {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('use_rag', useRAG.toString());
  formData.append('use_web_search', useWebSearch.toString());
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  const response = await apiClient.post<AnswerResponse>('/ask_problem_image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

/**
 * 資料一覧を取得
 */
export async function getDocuments(
  status?: string,
  subject?: string,
  limit: number = 50,
  offset: number = 0
): Promise<DocumentListResponse> {
  const response = await apiClient.get<DocumentListResponse>('/documents', {
    params: { status, subject, limit, offset },
  });
  return response.data;
}

/**
 * 資料を削除
 */
export async function deleteDocument(documentId: number): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}

/**
 * ヘルスチェック
 */
export async function healthCheck(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
}

