# 状態管理方針（案）

## グローバル状態（候補: React Context + Zustand）
- ライブラリ: Zustand（軽量・シンプル・型付け容易）
- 設定: useRAG, useWebSearch（初期は useWebSearch=false 固定・未実装）
- セッションID（任意）
- ドキュメント一覧のキャッシュ

## ローカル状態
- 入力中テキスト、選択中画像、ローディング状態
- 各モーダルの開閉

## 非同期通信
- API呼び出しは services 層に集約（axios）
- リトライ・タイムアウト・キャンセル対応（AbortController）

## エラーハンドリング
- UI: トースト/バナーで通知
- ログ: コンソール + 将来の収集を見据えたHook設計


