"""OCRサービス - DeepSeek-OCR連携"""
import aiohttp
from typing import Optional
from ..config import settings


class OCRService:
    """OCRサービス（DeepSeek-OCR API呼び出し）"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.ocr_url

    async def extract_text(self, image_bytes: bytes) -> str:
        """画像からMarkdown形式でテキスト抽出

        Args:
            image_bytes: 画像データ（バイナリ）

        Returns:
            抽出されたMarkdownテキスト

        Raises:
            aiohttp.ClientError: OCRサービスとの通信エラー
            ValueError: OCRサービスからのレスポンスが不正
        """
        try:
            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field(
                    'image',
                    image_bytes,
                    filename='image.png',
                    content_type='image/png'
                )

                async with session.post(
                    f"{self.base_url}/api/ocr",
                    data=form,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(
                            f"OCR failed with status {response.status}: {error_text}"
                        )

                    result = await response.json()
                    
                    if "markdown" not in result:
                        raise ValueError("OCR response missing 'markdown' field")
                    
                    return result["markdown"]

        except aiohttp.ClientError as e:
            raise ValueError(f"OCR service connection error: {e}")

    async def health_check(self) -> bool:
        """OCRサービスのヘルスチェック

        Returns:
            True: 正常, False: 異常
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False

