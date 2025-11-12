/**
 * 資料管理画面
 */
import { useState, useEffect } from 'react';
import { getDocuments, deleteDocument } from '../services/api';
import { uploadDocument } from '../services/n8nApi';
import type { DocumentInfo } from '../types';

export const DocumentManager = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('');

  // 資料一覧を取得
  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDocuments(filterStatus || undefined);
      setDocuments(response.documents);
    } catch (err) {
      setError('資料の取得に失敗しました');
      console.error('Error loading documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [filterStatus]);

  // ファイルアップロード
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // ファイル検証
    const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      setError('許可されていないファイル形式です（PDF, PNG, JPG, JPEG のみ）');
      return;
    }

    const maxSizeMB = 100;
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`ファイルサイズは${maxSizeMB}MB以下にしてください`);
      return;
    }

    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      alert('資料のアップロードを開始しました。処理には時間がかかる場合があります。');
      // 少し待ってからリロード
      setTimeout(loadDocuments, 2000);
    } catch (err) {
      setError('資料のアップロードに失敗しました');
      console.error('Error uploading document:', err);
    } finally {
      setUploading(false);
      // ファイル入力をリセット
      e.target.value = '';
    }
  };

  // 資料削除
  const handleDelete = async (id: number, filename: string) => {
    if (!confirm(`"${filename}" を削除しますか？`)) return;

    try {
      await deleteDocument(id);
      alert('資料を削除しました');
      loadDocuments();
    } catch (err) {
      setError('資料の削除に失敗しました');
      console.error('Error deleting document:', err);
    }
  };

  // ステータスの日本語表示
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'processing':
        return '処理中';
      case 'completed':
        return '完了';
      case 'failed':
        return '失敗';
      default:
        return status;
    }
  };

  // ステータスの色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing':
        return 'text-yellow-500';
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">資料管理</h2>

      {/* アップロードセクション */}
      <div className="mb-6 p-4 bg-gray-800 rounded-lg">
        <h3 className="text-lg font-semibold mb-3">資料をアップロード</h3>
        <div className="flex items-center gap-4">
          <label className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded cursor-pointer disabled:opacity-50">
            {uploading ? 'アップロード中...' : 'ファイルを選択'}
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
          <span className="text-sm text-gray-400">
            PDF, PNG, JPG, JPEG （最大100MB）
          </span>
        </div>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded text-red-200">
          {error}
        </div>
      )}

      {/* フィルター */}
      <div className="mb-4 flex items-center gap-4">
        <label className="text-sm text-gray-400">ステータス:</label>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-1 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
        >
          <option value="">すべて</option>
          <option value="completed">完了</option>
          <option value="processing">処理中</option>
          <option value="failed">失敗</option>
        </select>
        <button
          onClick={loadDocuments}
          className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
        >
          🔄 更新
        </button>
      </div>

      {/* 資料一覧 */}
      {loading ? (
        <div className="text-center py-8 text-gray-400">読み込み中...</div>
      ) : documents.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          資料がありません。上記からファイルをアップロードしてください。
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold">ファイル名</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">科目</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">ステータス</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">チャンク数</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">作成日時</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">操作</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-t border-gray-700 hover:bg-gray-750">
                  <td className="px-4 py-3 text-sm">{doc.filename}</td>
                  <td className="px-4 py-3 text-sm">{doc.subject || '-'}</td>
                  <td className={`px-4 py-3 text-sm font-semibold ${getStatusColor(doc.status)}`}>
                    {getStatusLabel(doc.status)}
                  </td>
                  <td className="px-4 py-3 text-sm">{doc.chunk_count}</td>
                  <td className="px-4 py-3 text-sm">
                    {new Date(doc.created_at).toLocaleString('ja-JP')}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <button
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      className="px-3 py-1 bg-red-600 hover:bg-red-500 rounded text-xs"
                    >
                      削除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

