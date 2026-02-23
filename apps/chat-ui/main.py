"""
チャット UI: Investor Agent とのやりとりが見える Web 画面
"""
import os
from pathlib import Path

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import httpx


class AskBody(BaseModel):
    question: str

INVESTOR_AGENT_URL = os.environ.get("INVESTOR_AGENT_URL", "http://investor-agent:8000").rstrip("/")
ASK_URL = f"{INVESTOR_AGENT_URL}/ask"

app = FastAPI(title="Investor Agent Chat UI")
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/ask")
async def api_ask(body: AskBody):
    if not body.question or not body.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(ASK_URL, json={"question": body.question.strip()})
            r.raise_for_status()
            body = r.json()
            return {"answer": body.get("answer", ""), "model": body.get("model", "")}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
