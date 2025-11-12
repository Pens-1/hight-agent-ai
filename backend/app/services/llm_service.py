"""LLMサービス - Ollama連携"""
import aiohttp
from typing import Optional
from ..config import settings


class LLMService:
    """LLMサービス（Ollama API呼び出し）"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.base_url = base_url or settings.ollama_url
        self.model = model or settings.ollama_model

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Ollamaで文章生成

        Args:
            prompt: プロンプト
            system: システムメッセージ
            temperature: 温度パラメータ（デフォルト: 0.7）
            max_tokens: 最大トークン数

        Returns:
            生成されたテキスト

        Raises:
            ValueError: Ollamaとの通信エラー
        """
        temperature = temperature or settings.llm_temperature

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                }

                if system:
                    payload["system"] = system

                if max_tokens:
                    payload["options"] = {"num_predict": max_tokens}

                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(
                            f"Ollama generate failed with status {response.status}: {error_text}"
                        )

                    result = await response.json()
                    
                    if "response" not in result:
                        raise ValueError("Ollama response missing 'response' field")
                    
                    return result["response"]

        except aiohttp.ClientError as e:
            raise ValueError(f"Ollama connection error: {e}")

    async def classify_subject(self, text: str) -> str:
        """資料の科目分類

        Args:
            text: 資料のテキスト（最初の2000文字程度）

        Returns:
            分類された科目名
        """
        # 最初の2000文字のみを使用
        text_sample = text[:2000]

        prompt = f"""以下の授業資料の内容を分析し、最も適切な科目を1つ選んでください。

資料内容:
{text_sample}

科目リスト:
- 数学
- 物理(力学)
- 物理(電磁気)
- 物理(熱力学)
- 物理(量子力学)
- 化学
- 生物学
- 情報科学
- 工学
- その他

回答は科目名のみを出力してください。"""

        system_message = "あなたは授業資料を分類する専門家です。与えられた資料の内容から科目を特定してください。"

        result = await self.generate(
            prompt=prompt,
            system=system_message,
            temperature=0.3  # 分類タスクなので低めの温度
        )

        # 結果をクリーンアップ（前後の空白や句読点を除去）
        return result.strip().rstrip("。、")

    async def health_check(self) -> bool:
        """Ollamaのヘルスチェック

        Returns:
            True: 正常, False: 異常
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # モデルが存在するか確認
                        models = data.get("models", [])
                        return any(m.get("name") == self.model for m in models)
                    return False
        except Exception:
            return False

