"""本地规则翻译引擎 — 不需要 AI，纯正则匹配"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class TranslationResult:
    source_code: str
    translated_code: str
    source_lang: str
    target_lang: str
    notes: str = ""


# ─── 通用替换规则 ─────────────────────────────────────────────

# Python → JavaScript
_PY_TO_JS: list[tuple[str, str]] = [
    # 常量
    (r'\bTrue\b', 'true'),
    (r'\bFalse\b', 'false'),
    (r'\bNone\b', 'null'),
    # print
    (r'print\s*\((.+)\)', r'console.log(\1)'),
    # len()
    (r'len\((.+)\)', r'\1.length'),
    # string methods
    (r'\.upper\(\)', '.toUpperCase()'),
    (r'\.lower\(\)', '.toLowerCase()'),
    (r'\.strip\(\)', '.trim()'),
    (r'\.split\(([^)]+)\)', r'.split(\1)'),
    (r'\.join\(([^)]+)\)', r'.join(\1)'),
    (r'\.replace\(([^,]+),\s*([^)]+)\)', r'.replace(\1, \2)'),
    (r'\.find\(([^)]+)\)', r'.indexOf(\1)'),
    (r'\.startswith\(([^)]+)\)', r'.startsWith(\1)'),
    (r'\.endswith\(([^)]+)\)', r'.endsWith(\1)'),
    (r'\.append\(([^)]+)\)', r'.push(\1)'),
    # 类型转换
    (r'\bint\(([^)]+)\)', r'parseInt(\1)'),
    (r'\bfloat\(([^)]+)\)', r'parseFloat(\1)'),
    (r'\bstr\(([^)]+)\)', r'String(\1)'),
    (r'\bbool\(([^)]+)\)', r'Boolean(\1)'),
    # range
    (r'range\(([^)]+)\)', r'Array.from({length: \1}, (_, i) => i)'),
    # 列表推导式
    (r'\[(\w+)\s+for\s+(\w+)\s+in\s+(\w+)\s+if\s+([^\]]+)\]',
     r'\3.filter(\2 => \4).map(\2 => \1)'),
    (r'\[(\w+)\s+for\s+(\w+)\s+in\s+(\w+)\]',
     r'\3.map(\2 => \1)'),
    # f-string → template literal
    (r"""f['"]\{(.+?)\}""", r'`${\1}`'),
]

# Python → Go
_PY_TO_GO: list[tuple[str, str]] = [
    (r'\bTrue\b', 'true'),
    (r'\bFalse\b', 'false'),
    (r'\bNone\b', 'nil'),
    (r'print\s*\((.+)\)', r'fmt.Println(\1)'),
    (r'len\((.+)\)', r'len(\1)'),
    (r'\.upper\(\)', '.Upper()'),
    (r'\.lower\(\)', '.Lower()'),
    (r'\.strip\(\)', '.TrimSpace()'),
    (r'\.append\(([^)]+)\)', r'append(_, \1)'),
    (r'\bint\(([^)]+)\)', r'int(\1)'),
    (r'\bfloat\(([^)]+)\)', r'float64(\1)'),
    (r'\bstr\(([^)]+)\)', r'str(\1)'),
    (r'\brange\(([^)]+)\)', r'// range(\1) — 需手动转换'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*(\w+):', r'func \1(\2) \3 {'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*:', r'func \1(\2) {'),
    (r'class\s+(\w+)\s*:', r'// 类 \1'),
    (r'if\s+__name__\s*==\s*["\']__main__["\']\s*:', 'func main() {'),
]

# Python → Java
_PY_TO_JAVA: list[tuple[str, str]] = [
    (r'\bTrue\b', 'true'),
    (r'\bFalse\b', 'false'),
    (r'\bNone\b', 'null'),
    (r'print\s*\((.+)\)', r'System.out.println(\1)'),
    (r'len\(([^)]+)\)', r'\1.length()'),
    (r'\.upper\(\)', '.toUpperCase()'),
    (r'\.lower\(\)', '.toLowerCase()'),
    (r'\.strip\(\)', '.trim()'),
    (r'\bint\(([^)]+)\)', r'(int) (\1)'),
    (r'\bfloat\(([^)]+)\)', r'(double) (\1)'),
    (r'\bstr\(([^)]+)\)', r'String.valueOf(\1)'),
    (r'\.append\(([^)]+)\)', r'.add(\1)'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*(\w+):',
     r'public \3 \1(\2) {'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*:',
     r'public void \1(\2) {'),
    (r'class\s+(\w+)\s*:', r'public class \1 {'),
]

# Python → TypeScript
_PY_TO_TS: list[tuple[str, str]] = [
    (r'\bTrue\b', 'true'),
    (r'\bFalse\b', 'false'),
    (r'\bNone\b', 'null'),
    (r'print\s*\((.+)\)', r'console.log(\1)'),
    (r'len\((.+)\)', r'\1.length'),
    (r'\.upper\(\)', '.toUpperCase()'),
    (r'\.lower\(\)', '.toLowerCase()'),
    (r'\.strip\(\)', '.trim()'),
    (r'\.append\(([^)]+)\)', r'.push(\1)'),
    (r'\bint\(([^)]+)\)', r'parseInt(\1)'),
    (r'\bfloat\(([^)]+)\)', r'parseFloat(\1)'),
    (r'\bstr\(([^)]+)\)', r'String(\1)'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*(\w+):',
     r'function \1(\2): \3 {'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*:',
     r'function \1(\2) {'),
    (r'class\s+(\w+)\s*:', r'class \1 {'),
    (r'#(.+)', r'//\1'),
]

# Python → Rust
_PY_TO_RS: list[tuple[str, str]] = [
    (r'\bTrue\b', 'true'),
    (r'\bFalse\b', 'false'),
    (r'\bNone\b', 'None'),
    (r'print\s*\((.+)\)', r'println!("{}", \1)'),
    (r'len\(([^)]+)\)', r'\1.len()'),
    (r'\.upper\(\)', '.to_upper()'),
    (r'\.lower\(\)', '.to_lower()'),
    (r'\.strip\(\)', '.trim()'),
    (r'\.append\(([^)]+)\)', r'.push(\1)'),
    (r'\bint\(([^)]+)\)', r'\1.parse::<i32>().unwrap()'),
    (r'\bstr\(([^)]+)\)', r'\1.to_string()'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*(\w+):',
     r'fn \1(\2) -> \3 {'),
    (r'def\s+(\w+)\s*\(([^)]*)\)\s*:',
     r'fn \1(\2) {'),
    (r'class\s+(\w+)\s*:', r'// 类 \1'),
    (r'#(.+)', r'//\1'),
]

# JavaScript → Python
_JS_TO_PY: list[tuple[str, str]] = [
    (r'\btrue\b', 'True'),
    (r'\bfalse\b', 'False'),
    (r'\bnull\b', 'None'),
    (r'\bundefined\b', 'None'),
    (r'console\.log\((.+)\)', r'print(\1)'),
    (r'\.length\b', '.length()'),  # 注意: JS .length 是属性
    (r'\.toUpperCase\(\)', '.upper()'),
    (r'\.toLowerCase\(\)', '.lower()'),
    (r'\.trim\(\)', '.strip()'),
    (r'\.push\(([^)]+)\)', r'.append(\1)'),
    (r'\.indexOf\(([^)]+)\)', r'.find(\1)'),
    (r'\.startsWith\(([^)]+)\)', r'.startswith(\1)'),
    (r'\.endsWith\(([^)]+)\)', r'.endswith(\1)'),
    (r'parseInt\(([^)]+)\)', r'int(\1)'),
    (r'parseFloat\(([^)]+)\)', r'float(\1)'),
    (r'String\(([^)]+)\)', r'str(\1)'),
    (r'function\s+(\w+)\s*\(([^)]*)\)\s*\{',
     r'def \1(\2):'),
    (r'const\s+(\w+)\s*=\s*(\w+)\s*=>\s*\{',
     r'def \1(\2):'),
    (r'class\s+(\w+)\s*\{', r'class \1:'),
    (r'//(.+)', r'#\1'),
    (r'===', '=='),
    (r'!==', '!='),
]

# Go → Python
_GO_TO_PY: list[tuple[str, str]] = [
    (r'\btrue\b', 'True'),
    (r'\bfalse\b', 'False'),
    (r'\bnil\b', 'None'),
    (r'fmt\.Println\((.+)\)', r'print(\1)'),
    (r'func\s+(\w+)\s*\(([^)]*)\)\s*\w+\s*\{', r'def \1(\2):'),
    (r'func\s+(\w+)\s*\(([^)]*)\)\s*\{', r'def \1(\2):'),
    (r'func\s+main\(\)\s*\{', 'if __name__ == "__main__":'),
]

# ─── 语言对映射 ─────────────────────────────────────────────

_RULES_MAP: dict[str, dict[str, list[tuple[str, str]]]] = {
    "python": {
        "javascript": _PY_TO_JS,
        "typescript": _PY_TO_TS,
        "go": _PY_TO_GO,
        "java": _PY_TO_JAVA,
        "rust": _PY_TO_RS,
    },
    "javascript": {
        "python": _JS_TO_PY,
    },
    "go": {
        "python": _GO_TO_PY,
    },
}


class LocalTranslator:
    """本地规则翻译器 — 无需 API Key"""

    def translate(
        self,
        code: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        rules = _RULES_MAP.get(source_lang, {}).get(target_lang)

        if not rules:
            note = (
                f"本地模式暂不支持 {source_lang} → {target_lang} 翻译。"
                f"目前支持的组合: {', '.join(_RULES_MAP.keys())} → 目标语言"
            )
            return TranslationResult(
                source_code=code,
                translated_code=f"/* {note} */\n{code}",
                source_lang=source_lang,
                target_lang=target_lang,
                notes=note,
            )

        result = code
        applied = []
        for pattern, replacement in rules:
            new_result = re.sub(pattern, replacement, result)
            if new_result != result:
                applied.append(pattern)
                result = new_result

        notes = f"本地规则翻译 ({len(applied)} 条规则匹配)"
        if not applied:
            notes = "没有匹配到特定规则，已原样输出"

        return TranslationResult(
            source_code=code,
            translated_code=result,
            source_lang=source_lang,
            target_lang=target_lang,
            notes=notes,
        )
