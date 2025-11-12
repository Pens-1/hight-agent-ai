/**
 * n8n Webhook との通信
 */
import axios from 'axios';

const N8N_WEBHOOK_URL = import.meta.env.VITE_N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/upload_document';

/**
 * 資料をアップロード（n8nワークフロー）
 */
export async function uploadDocument(file: File): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);

  await axios.post(N8N_WEBHOOK_URL, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 1分
  });
}

