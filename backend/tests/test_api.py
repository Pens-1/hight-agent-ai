"""APIエンドポイントのテスト"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "hight-agent-ai backend running"


def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "ollama" in data["services"]
    assert "ocr" in data["services"]


def test_ask_problem_text_without_question():
    """質問なしのテキスト問題送信（バリデーションエラー）"""
    response = client.post(
        "/api/ask_problem_text",
        json={"question": ""}
    )
    # pydantic validation error
    assert response.status_code == 422


def test_documents_list():
    """資料一覧取得のテスト"""
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)
    assert isinstance(data["total"], int)


def test_documents_list_with_filters():
    """フィルタ付き資料一覧取得のテスト"""
    response = client.get("/api/documents?status=completed&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data

