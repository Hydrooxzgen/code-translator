"""直接运行: python main.py"""

import sys
from pathlib import Path

# 让 Python 找到 src 下的包
sys.path.insert(0, str(Path(__file__).parent / "src"))

from code_translator.web import app

import uvicorn

if __name__ == "__main__":
    print("🚀 启动 Web 界面: http://127.0.0.1:8000")
    print("按 Ctrl+C 停止服务")
    uvicorn.run(app, host="127.0.0.1", port=8000)
