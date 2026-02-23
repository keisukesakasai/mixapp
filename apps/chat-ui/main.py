"""
チャット UI: Redis にスタックされた Investor Agent とのやりとりを参照して表示するだけ
"""
import json
import os
from pathlib import Path

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

REDIS_KEY_MESSAGES = "investor_agent:messages"
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

app = FastAPI(title="Investor Agent Chat UI")
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.state.redis: redis.Redis | None = None


@app.on_event("startup")
async def startup():
    try:
        app.state.redis = redis.from_url(REDIS_URL, decode_responses=True)
        await app.state.redis.ping()
    except Exception:
        app.state.redis = None


@app.on_event("shutdown")
async def shutdown():
    if app.state.redis:
        await app.state.redis.aclose()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/messages")
async def get_messages():
    """Redis にスタックされたやりとりを古い順で返す"""
    if not app.state.redis:
        return {"messages": [], "error": "Redis not connected"}
    try:
        raw = await app.state.redis.lrange(REDIS_KEY_MESSAGES, 0, -1)
        messages = []
        for s in raw:
            try:
                messages.append(json.loads(s))
            except json.JSONDecodeError:
                continue
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
