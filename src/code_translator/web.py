"""Web 图形界面 — FastAPI"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from code_translator.config import load_config
from code_translator.translator import Translator

app = FastAPI(title="Code Translator")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/translate")
async def api_translate(request: Request):
    from pydantic import BaseModel

    class TranslateRequest(BaseModel):
        code: str
        source_lang: str
        target_lang: str
        api_key: str = ""
        base_url: str = ""
        model: str = ""
        mode: str = "local"  # "local" 或 "ai"

    body = TranslateRequest.model_validate(await request.json())

    # 本地模式 — 不需要 API Key
    if body.mode == "local":
        from code_translator.local_translator import LocalTranslator
        translator = LocalTranslator()
        result = translator.translate(body.code, body.source_lang, body.target_lang)
        return {
            "translated_code": result.translated_code,
            "model": "local-rules",
            "notes": result.notes,
        }

    # AI 模式
    try:
        config = load_config(
            api_key=body.api_key or None,
            base_url=body.base_url or None,
            model=body.model or None,
        )
    except ValueError as e:
        return {"error": str(e)}

    translator = Translator(config)

    try:
        result = translator.translate(body.code, body.source_lang, body.target_lang)
    except RuntimeError as e:
        return {"error": str(e)}

    return {
        "translated_code": result.translated_code,
        "model": config.model,
    }


@app.get("/api/languages")
async def api_languages():
    from code_translator.languages import LANGUAGE_DISPLAY_NAMES

    return {"languages": LANGUAGE_DISPLAY_NAMES}
