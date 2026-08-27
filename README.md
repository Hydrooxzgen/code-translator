# code-translator

跨编程语言的代码翻译器 —— 输入一种语言的代码，输出另一种语言的等价代码。

## ✨ 特性

- 🔤 支持多种编程语言互译（Python ↔ JavaScript ↔ Go ↔ Java ...）
- 🤖 基于 LLM 的智能翻译，保持语义等价
- 📦 命令行工具，简单易用
- 🔌 可扩展的语言支持

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/code-translator.git
cd code-translator

# 安装依赖
uv sync
```

### 使用

```bash
# 翻译 Python 代码为 JavaScript
uv run code-translator translate -s python -t javascript input.py

# 翻译代码片段
uv run code-translator translate -s python -t go --code "def hello(): print('Hello')"
```

## 📁 项目结构

```
code-translator/
├── pyproject.toml
├── src/
│   └── code_translator/
│       ├── __init__.py
│       ├── cli.py              # CLI 入口
│       ├── translator.py       # 核心翻译引擎
│       ├── languages/          # 各语言定义
│       └── prompts/            # LLM prompt 模板
├── tests/
└── examples/
```

## 🛠️ 开发

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest
```

## 📄 License

MIT
