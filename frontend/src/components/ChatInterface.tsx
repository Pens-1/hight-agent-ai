/**
 * チャットインターフェース
 */
import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../store/useChatStore';
import { useSettings } from '../store/useSettings';
import { askProblemText, askProblemImage } from '../services/api';
import { MarkdownRenderer } from './MarkdownRenderer';
import type { Message } from '../types';

export const ChatInterface = () => {
  const { messages, isLoading, sessionId, addMessage, setLoading } = useChatStore();
  const { useRAG } = useSettings();
  const [input, setInput] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 自動スクロール
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 画像選択
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // 画像クリア
  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // テキスト送信
  const handleTextSubmit = async () => {
    if (!input.trim() && !imageFile) return;

    setLoading(true);

    try {
      // ユーザーメッセージを追加
      const userMessage: Message = {
        id: crypto.randomUUID(),
        type: 'user',
        content: input || '（画像を送信しました）',
        image: imagePreview || undefined,
        timestamp: new Date(),
      };
      addMessage(userMessage);

      // API呼び出し
      let response;
      if (imageFile) {
        response = await askProblemImage(imageFile, useRAG, false, sessionId);
      } else {
        response = await askProblemText(input, useRAG, false, sessionId);
      }

      // アシスタントメッセージを追加
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        type: 'assistant',
        content: response.answer,
        referencedDocs: response.referenced_documents,
        timestamp: new Date(),
        processingTimeMs: response.processing_time_ms,
      };
      addMessage(assistantMessage);

      // 入力をクリア
      setInput('');
      clearImage();
    } catch (error) {
      console.error('Error sending message:', error);
      
      // エラーメッセージを表示
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        type: 'assistant',
        content: `エラーが発生しました: ${error instanceof Error ? error.message : '不明なエラー'}`,
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Enterキーで送信
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleTextSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* メッセージ一覧 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">hight-agent-ai へようこそ</p>
            <p className="text-sm">問題を入力または画像をアップロードして質問してください</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-100'
                }`}
              >
                {message.image && (
                  <img
                    src={message.image}
                    alt="Uploaded"
                    className="max-w-sm rounded mb-2"
                  />
                )}
                <MarkdownRenderer content={message.content} />
                {message.referencedDocs && message.referencedDocs.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <p className="text-xs text-gray-400 mb-2">参照資料:</p>
                    {message.referencedDocs.map((doc, idx) => (
                      <div key={idx} className="text-xs text-gray-400 mb-1">
                        📄 {doc.filename} {doc.subject && `(${doc.subject})`}
                      </div>
                    ))}
                  </div>
                )}
                {message.processingTimeMs && (
                  <div className="mt-2 text-xs text-gray-400">
                    処理時間: {(message.processingTimeMs / 1000).toFixed(2)}秒
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce">●</div>
                <div className="animate-bounce" style={{ animationDelay: '0.1s' }}>●</div>
                <div className="animate-bounce" style={{ animationDelay: '0.2s' }}>●</div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 入力エリア */}
      <div className="border-t border-gray-800 p-4">
        {imagePreview && (
          <div className="mb-2 relative inline-block">
            <img src={imagePreview} alt="Preview" className="max-w-xs rounded" />
            <button
              onClick={clearImage}
              className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600"
            >
              ×
            </button>
          </div>
        )}
        <div className="flex items-end gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            title="画像をアップロード"
          >
            📷
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            placeholder="質問を入力してください..."
            className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded resize-none focus:outline-none focus:border-blue-500 disabled:opacity-50"
            rows={2}
          />
          <button
            onClick={handleTextSubmit}
            disabled={isLoading || (!input.trim() && !imageFile)}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            送信
          </button>
        </div>
      </div>
    </div>
  );
};

