"""命令行界面"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from code_translator.config import load_config
from code_translator.translator import Translator

app = typer.Typer(
    name="code-translator",
    help="跨编程语言的代码翻译器 🔤",
    no_args_is_help=True,
)
console = Console()


def _common_options(f):
    """翻译命令的公共选项装饰器"""
    import functools

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    wrapper = typer.option("--api-key", envvar="CODE_TRANSLATOR_API_KEY", help="API Key")(wrapper)
    wrapper = typer.option("--base-url", envvar="CODE_TRANSLATOR_BASE_URL", default=None, help="API Base URL")(wrapper)
    wrapper = typer.option("--model", envvar="CODE_TRANSLATOR_MODEL", default=None, help="模型名称")(wrapper)
    return wrapper


@app.command()
def translate(
    source_file: str = typer.Argument(None, help="输入文件路径"),
    source_lang: str = typer.Option(
        "-s", "--source-lang", help="源语言", prompt="源语言"
    ),
    target_lang: str = typer.Option(
        "-t", "--target-lang", help="目标语言", prompt="目标语言"
    ),
    code: str = typer.Option(None, "--code", "-c", help="直接输入代码片段"),
    output: str = typer.Option(None, "--output", "-o", help="输出文件路径"),
    api_key: str = typer.Option(None, "--api-key", envvar="CODE_TRANSLATOR_API_KEY", help="API Key (可选，本地模型不需要)"),
    base_url: str = typer.Option(None, "--base-url", envvar="CODE_TRANSLATOR_BASE_URL", help="API Base URL (如 Ollama: http://localhost:11434/v1)"),
    model: str = typer.Option(None, "--model", envvar="CODE_TRANSLATOR_MODEL", help="模型名称 (如 gpt-4o, llama3)"),
):
    """翻译代码从一种语言到另一种语言"""
    # 1. 获取源代码
    if code:
        source_code = code
    elif source_file:
        path = Path(source_file)
        if not path.exists():
            console.print(f"[red]❌ 文件不存在: {source_file}[/red]")
            raise typer.Exit(1)
        source_code = path.read_text(encoding="utf-8")
    else:
        # 从 stdin 读取
        if sys.stdin.isatty():
            console.print("[red]❌ 请提供源文件、--code 参数或通过管道输入代码[/red]")
            raise typer.Exit(1)
        source_code = sys.stdin.read()

    # 2. 加载配置 & 创建翻译器
    try:
        config = load_config(api_key=api_key, base_url=base_url, model=model)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)

    translator = Translator(config)

    # 3. 执行翻译
    console.print(f"🔄 翻译中: {source_lang} → {target_lang} (模型: {config.model})")
    with console.status("[bold green]LLM 正在翻译..."):
        try:
            result = translator.translate(source_code, source_lang, target_lang)
        except RuntimeError as e:
            console.print(f"[red]❌ {e}[/red]")
            raise typer.Exit(1)

    # 4. 输出结果
    console.print(
        Panel(
            Markdown(f"```{target_lang}\n{result.translated_code}\n```"),
            title=f"✅ {source_lang} → {target_lang}",
            border_style="green",
        )
    )

    # 5. 写入文件
    if output:
        Path(output).write_text(result.translated_code, encoding="utf-8")
        console.print(f"[dim]📄 已保存到 {output}[/dim]")


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="监听地址"),
    port: int = typer.Option(8000, "--port", "-p", help="监听端口"),
    reload: bool = typer.Option(False, "--reload", help="开发模式自动重载"),
):
    """启动 Web 图形界面"""
    import uvicorn

    console.print(f"[bold green]🚀 启动 Web 界面: http://{host}:{port}[/bold green]")
    console.print("[dim]按 Ctrl+C 停止服务[/dim]")
    uvicorn.run(
        "code_translator.web:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def languages():
    """列出支持的语言"""
    from code_translator.languages import LANGUAGE_DISPLAY_NAMES

    console.print("[bold]支持的语言:[/bold]")
    for key, name in LANGUAGE_DISPLAY_NAMES.items():
        console.print(f"  • {name} ({key})")


if __name__ == "__main__":
    app()
