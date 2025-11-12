#!/bin/bash
# セットアップスクリプト

set -e

echo "=== hight-agent-ai セットアップ ==="

# 環境変数ファイルの作成
if [ ! -f .env ]; then
    echo "📝 .env ファイルを作成します..."
    cat > .env << EOF
# Database
DB_PASSWORD=hight_agent_password

# n8n
N8N_PASSWORD=n8n_admin_password

# Ollama
OLLAMA_MODEL=qwen2.5:7b-instruct

# Embedding
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EOF
    echo "✅ .env ファイルを作成しました"
else
    echo "✅ .env ファイルは既に存在します"
fi

# Dockerコンテナの起動
echo ""
echo "🐳 Dockerコンテナを起動します..."
docker-compose up -d postgres ollama ocr-service

echo ""
echo "⏳ データベースの起動を待機中..."
sleep 10

# Ollamaモデルのダウンロード
echo ""
echo "🤖 Ollamaモデルをダウンロードします..."
echo "   (初回は時間がかかります。モデルサイズ: 約4GB)"
docker exec -it hight-ai-ollama ollama pull qwen2.5:7b-instruct || echo "⚠️  Ollamaモデルのダウンロードに失敗しました。手動で実行してください。"

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "次のステップ:"
echo "1. バックエンドとフロントエンドを起動:"
echo "   docker-compose up -d backend frontend"
echo ""
echo "2. n8nを起動（オプション）:"
echo "   docker-compose up -d n8n"
echo "   ブラウザで http://localhost:5678 にアクセス"
echo ""
echo "3. フロントエンドにアクセス:"
echo "   http://localhost:5173"
echo ""
echo "4. APIドキュメント:"
echo "   http://localhost:8000/docs"

