"""配置管理 — 环境变量 + CLI 参数合并"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM 连接配置"""

    api_key: str = ""
    base_url: str = "https://opencode.ai/zen/v1"
    model: str = "mimo-v2.5-free"


def load_config(
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> LLMConfig:
    """
    加载配置，优先级：CLI 参数 > 环境变量 > 默认值
    """
    return LLMConfig(
        api_key=api_key
        or os.environ.get("CODE_TRANSLATOR_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY", ""),
        base_url=base_url
        or os.environ.get("CODE_TRANSLATOR_BASE_URL", "")
        or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=model
        or os.environ.get("CODE_TRANSLATOR_MODEL", "")
        or os.environ.get("OPENAI_MODEL", "gpt-4o"),
    )
