"""核心翻译引擎"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from code_translator.config import LLMConfig
from code_translator.languages import LANGUAGE_DISPLAY_NAMES

# prompt 模板路径
_PROMPT_TEMPLATE = Path(__file__).parent / "prompts" / "translate.md"


@dataclass
class TranslationResult:
    """翻译结果"""

    source_code: str
    translated_code: str
    source_lang: str
    target_lang: str
    notes: str = ""


class Translator:
    """代码翻译器 — 基于 OpenAI 兼容协议的 LLM 翻译"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = OpenAI(
            api_key=config.api_key or "no-key",
            base_url=config.base_url,
        )

    def _build_prompt(self, code: str, source_lang: str, target_lang: str) -> str:
        """渲染翻译 prompt"""
        template = _PROMPT_TEMPLATE.read_text(encoding="utf-8")
        src_name = LANGUAGE_DISPLAY_NAMES.get(source_lang, source_lang)
        tgt_name = LANGUAGE_DISPLAY_NAMES.get(target_lang, target_lang)
        return (
            template.replace("{source_lang}", src_name)
            .replace("{target_lang}", tgt_name)
            .replace("{code}", code)
        )

    @staticmethod
    def _extract_code(raw: str, target_lang: str) -> str:
        """从 LLM 输出中提取代码块（去掉 markdown 代码围栏）"""
        # 尝试匹配 ```lang\n...\n``` 块
        pattern = rf"```(?:{target_lang})?\s*\n(.*?)```"
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            return match.group(1).strip()
        # 如果没有代码围栏，返回原始文本
        return raw.strip()

    def translate(
        self,
        code: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """
        翻译代码

        Args:
            code: 源代码
            source_lang: 源语言 (如 "python", "javascript")
            target_lang: 目标语言 (如 "go", "java")

        Returns:
            TranslationResult

        Raises:
            RuntimeError: LLM 调用失败
        """
        prompt = self._build_prompt(code, source_lang, target_lang)

        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的代码翻译器。只输出翻译后的代码，不要解释。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            raw_output = response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"LLM 调用失败: {e}") from e

        translated = self._extract_code(raw_output, target_lang)

        return TranslationResult(
            source_code=code,
            translated_code=translated,
            source_lang=source_lang,
            target_lang=target_lang,
        )
