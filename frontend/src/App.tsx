/**
 * メインアプリケーション
 */
import { useState } from 'react';
import { useSettings } from './store/useSettings';
import { useChatStore } from './store/useChatStore';
import { ChatInterface } from './components/ChatInterface';
import { DocumentManager } from './components/DocumentManager';

export const App = () => {
  const { useRAG, toggleRAG } = useSettings();
  const { clearMessages } = useChatStore();
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-gray-100">
      {/* ヘッダー */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-bold">hight-agent-ai</h1>
            <nav className="flex gap-2">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded ${
                  activeTab === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                💬 チャット
              </button>
              <button
                onClick={() => setActiveTab('documents')}
                className={`px-4 py-2 rounded ${
                  activeTab === 'documents'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                📚 資料管理
              </button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <span className="text-sm text-gray-300">RAG検索</span>
              <input
                type="checkbox"
                checked={useRAG}
                onChange={toggleRAG}
                className="w-4 h-4"
              />
            </label>
            <button
              onClick={clearMessages}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
              title="チャット履歴をクリア"
            >
              🗑️ クリア
            </button>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? <ChatInterface /> : <DocumentManager />}
      </main>

      {/* フッター */}
      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-2 text-xs text-gray-400 text-center">
        hight-agent-ai v0.1.0 - ローカル完結型学習支援AIエージェント
      </footer>
    </div>
  );
};

