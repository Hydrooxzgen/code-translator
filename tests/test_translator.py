"""翻译器测试"""

import pytest
from code_translator.config import LLMConfig, load_config
from code_translator.translator import Translator, TranslationResult


class TestLLMConfig:
    """LLMConfig 测试"""

    def test_config_with_api_key(self):
        """测试正常初始化"""
        config = LLMConfig(api_key="test-key", model="gpt-4o")
        assert config.api_key == "test-key"
        assert config.model == "gpt-4o"

    def test_config_without_api_key(self):
        """测试本地模型不需要 API Key"""
        config = LLMConfig(base_url="http://localhost:11434/v1", model="llama3")
        assert config.api_key == ""
        assert config.model == "llama3"

    def test_config_custom_base_url(self):
        """测试自定义 base_url"""
        config = LLMConfig(
            api_key="test-key",
            base_url="http://localhost:11434/v1",
            model="llama3",
        )
        assert config.base_url == "http://localhost:11434/v1"
        assert config.model == "llama3"


class TestLoadConfig:
    """load_config 测试"""

    def test_cli_params_override(self, monkeypatch):
        """测试 CLI 参数优先于环境变量"""
        monkeypatch.setenv("CODE_TRANSLATOR_API_KEY", "env-key")
        config = load_config(api_key="cli-key")
        assert config.api_key == "cli-key"

    def test_env_fallback(self, monkeypatch):
        """测试环境变量回退"""
        monkeypatch.setenv("CODE_TRANSLATOR_API_KEY", "env-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        config = load_config()
        assert config.api_key == "env-key"


class TestTranslator:
    """Translator 类的测试"""

    def test_extract_code_with_fence(self):
        """测试从 markdown 代码块中提取代码"""
        raw = '```python\nprint("hello")\n```'
        result = Translator._extract_code(raw, "python")
        assert result == 'print("hello")'

    def test_extract_code_without_fence(self):
        """测试无代码围栏时直接返回"""
        raw = 'print("hello")'
        result = Translator._extract_code(raw, "python")
        assert result == 'print("hello")'
