"""命令行界面"""

import typer
from rich.console import Console

app = typer.Typer(
    name="code-translator",
    help="跨编程语言的代码翻译器 🔤",
    no_args_is_help=True,
)
console = Console()


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
):
    """翻译代码从一种语言到另一种语言"""
    console.print(f"🔄 翻译中: {source_lang} → {target_lang}")
    # TODO: 实现翻译逻辑
    console.print("[yellow]⚠️ 翻译引擎尚未实现[/yellow]")


@app.command()
def languages():
    """列出支持的语言"""
    from code_translator.languages import SUPPORTED_LANGUAGES

    console.print("[bold]支持的语言:[/bold]")
    for lang in SUPPORTED_LANGUAGES:
        console.print(f"  • {lang}")


if __name__ == "__main__":
    app()
