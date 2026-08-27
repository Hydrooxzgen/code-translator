"""翻译器测试"""

import pytest
from code_translator.translator import Translator, TranslationResult


class TestTranslator:
    """Translator 类的测试"""

    def test_translator_init(self):
        """测试翻译器初始化"""
        t = Translator()
        assert t.model == "gpt-4o"

    def test_translate_not_implemented(self):
        """测试未实现时抛出异常"""
        t = Translator()
        with pytest.raises(NotImplementedError):
            t.translate("print('hello')", "python", "javascript")
