"""OCR処理モジュール"""
import io
from PIL import Image
import pytesseract
from typing import Optional


class OCRProcessor:
    """OCR処理クラス（Tesseract OCR使用）"""

    def __init__(self, lang: str = "jpn+eng"):
        """
        Args:
            lang: 使用言語（デフォルト: 日本語+英語）
        """
        self.lang = lang

    def process_image(self, image_bytes: bytes) -> str:
        """画像からテキストを抽出

        Args:
            image_bytes: 画像バイナリデータ

        Returns:
            抽出されたテキスト（Markdown形式）

        Raises:
            ValueError: 画像の読み込みまたはOCR処理に失敗した場合
        """
        try:
            # バイナリデータをPIL Imageに変換
            image = Image.open(io.BytesIO(image_bytes))

            # グレースケールに変換（OCR精度向上のため）
            if image.mode != 'L':
                image = image.convert('L')

            # Tesseract OCRで文字認識
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config='--psm 6'  # Assume a single uniform block of text
            )

            # Markdown形式に整形
            markdown = self._format_as_markdown(text)

            return markdown

        except Exception as e:
            raise ValueError(f"OCR processing failed: {e}")

    def _format_as_markdown(self, text: str) -> str:
        """テキストをMarkdown形式に整形

        Args:
            text: 抽出されたテキスト

        Returns:
            Markdown形式のテキスト
        """
        # 空行を削除し、整形
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return "# OCR結果\n\n（テキストが検出されませんでした）"

        # 簡易的なMarkdown整形
        markdown_lines = ["# OCR抽出結果\n"]
        
        for line in lines:
            # 数式らしきパターン（簡易判定）
            if any(char in line for char in ['=', '+', '-', '×', '÷', '∫', '∑', '√']):
                # 数式として扱う（ブロック数式）
                markdown_lines.append(f"$$\n{line}\n$$\n")
            else:
                # 通常のテキスト
                markdown_lines.append(f"{line}\n")

        return "\n".join(markdown_lines)

    def health_check(self) -> bool:
        """OCRエンジンの動作確認

        Returns:
            True: 正常, False: 異常
        """
        try:
            # ダミー画像でテスト
            test_image = Image.new('L', (100, 50), color=255)
            pytesseract.image_to_string(test_image, lang=self.lang)
            return True
        except Exception:
            return False

