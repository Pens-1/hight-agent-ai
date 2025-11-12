#!/bin/bash
# データベースクリーンアップスクリプト

set -e

echo "=== データベースクリーンアップ ==="
echo "⚠️  警告: すべてのデータが削除されます！"
read -p "続行しますか？ (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "キャンセルしました"
    exit 0
fi

echo ""
echo "🗑️  データベースをクリーンアップします..."

# データベースコンテナを停止・削除
docker-compose down postgres

# ボリュームを削除
docker volume rm hight-agent-ai_postgres_data 2>/dev/null || echo "ボリュームは存在しません"

# 再起動
docker-compose up -d postgres

echo ""
echo "⏳ データベースの起動を待機中..."
sleep 10

echo "✅ クリーンアップ完了！"

