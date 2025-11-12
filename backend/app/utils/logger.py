"""ロギング設定"""
import logging
import sys


def setup_logger(name: str = "hight-agent-ai", level: int = logging.INFO) -> logging.Logger:
    """ロガーをセットアップ

    Args:
        name: ロガー名
        level: ログレベル

    Returns:
        設定済みロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # ハンドラが既に設定されている場合はスキップ
    if logger.handlers:
        return logger

    # コンソールハンドラ
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # フォーマッタ
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

