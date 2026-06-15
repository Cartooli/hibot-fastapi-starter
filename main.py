"""hibot-fastapi-starter — a tiny text toolkit.

Type some text, the server counts words/characters/lines and tidies the
whitespace, then shows the result. No database, no API keys, no accounts.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sanitize import clean_text, MAX_LEN

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Hi Bot — Text Toolkit", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
# Jinja2 autoescaping is ON by default for .html — that's what keeps user text safe.
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def analyze(text: str) -> dict:
    """Pure text stats — easy to read, easy to extend with your own tools."""
    words = text.split()
    cleaned = " ".join(words)  # collapse runs of whitespace into single spaces
    return {
        "characters": len(text),
        "words": len(words),
        "lines": text.count("\n") + 1 if text else 0,
        "cleaned": cleaned,
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"text": "", "result": None, "max_len": MAX_LEN}
    )


@app.post("/", response_class=HTMLResponse)
async def process(request: Request, text: str = Form("")):
    safe = clean_text(text)          # normalize + bound the raw input
    result = analyze(safe)           # work only with the cleaned value
    return templates.TemplateResponse(
        request, "index.html", {"text": safe, "result": result, "max_len": MAX_LEN}
    )


def _render_doc(request: Request, title: str, filename: str) -> HTMLResponse:
    content = (BASE_DIR / filename).read_text(encoding="utf-8")
    return templates.TemplateResponse(
        request, "doc.html", {"title": title, "content": content}
    )


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return _render_doc(request, "Terms of Service", "TERMS_OF_SERVICE.md")


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return _render_doc(request, "Privacy Policy", "PRIVACY_POLICY.md")
