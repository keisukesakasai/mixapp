"""
Investor Agent: どの株を買うべきか等の投資相談に答える LLM Agent API
OpenAI 対応。応答は Redis にスタックし、UI はそれを参照する。
"""
import json
import os
from pathlib import Path
from time import time

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

REDIS_KEY_SESSION_IDS = "investor_agent:session_ids"


def _session_key(session_id: str) -> str:
    return f"investor_agent:session:{session_id}"

# リポジトリルートの .env を読む（どこから実行しても）
_THIS_DIR = Path(__file__).resolve().parent
_ENV_CANDIDATES = [_THIS_DIR / ".env", _THIS_DIR.parent.parent / ".env"]

SYSTEM_PROMPT = """あなたは Investor Agent（投資アドバイザーエージェント）です。
ユーザーから「今買うべき株」「おすすめ銘柄」などの質問に対して、一般的な市場のトレンドや
セクターの観点から簡潔に回答してください。必ず次の注意書きを回答の最後に含めてください：
「本回答は投資助言ではありません。投資判断はご自身の責任で行ってください。」
回答は日本語で、簡潔に（長くても 300 字程度）まとめてください。"""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(p) for p in _ENV_CANDIDATES if p.exists()],
        env_file_encoding="utf-8",
        extra="ignore",
    )
    openai_api_key: str = ""
    openai_base_url: str | None = None
    model: str = "gpt-4o-mini"
    port: int = 8000
    redis_url: str = "redis://redis:6379/0"


# 質問が実質ないとみなす文言（LLM を呼ばず 400 を返す）
NO_QUESTION_PLACEHOLDERS = frozenset({"（質問なし）", "(質問なし)", "（なし）", "(なし)"})


class AskRequest(BaseModel):
    question: str
    session_id: str = "default"


class AskResponse(BaseModel):
    answer: str
    model: str


def get_openai_client() -> AsyncOpenAI:
    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return AsyncOpenAI(**kwargs)


async def get_completion(user_message: str) -> tuple[str, str]:
    """
    プロバイダに応じて LLM 完了を取得。現在は OpenAI のみ。
    他モデル追加例: if settings.model.startswith("gemini"): return await _gemini_completion(...)
    """
    client = app.state.openai_client
    if not client:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
    completion = await client.chat.completions.create(
        model=settings.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=512,
    )
    answer = completion.choices[0].message.content or ""
    return answer, completion.model


settings = Settings()
app = FastAPI(title="Investor Agent", description="投資相談用 LLM Agent API")
app.state.openai_client = None
app.state.redis: redis.Redis | None = None


async def push_message(question: str, answer: str, model: str, session_id: str) -> None:
    if not app.state.redis:
        return
    sid = (session_id or "default").strip() or "default"
    payload = json.dumps({
        "question": question,
        "answer": answer,
        "model": model,
        "timestamp": round(time(), 3),
    }, ensure_ascii=False)
    key = _session_key(sid)
    await app.state.redis.rpush(key, payload)
    await app.state.redis.sadd(REDIS_KEY_SESSION_IDS, sid)


@app.on_event("startup")
async def startup():
    if settings.openai_api_key:
        app.state.openai_client = get_openai_client()
    try:
        app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)
        await app.state.redis.ping()
    except Exception:
        app.state.redis = None


@app.on_event("shutdown")
async def shutdown():
    if app.state.openai_client:
        await app.state.openai_client.close()
    if app.state.redis:
        await app.state.redis.aclose()


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "investor"}


def _is_no_question(q: str) -> bool:
    s = q.strip()
    return not s or s in NO_QUESTION_PLACEHOLDERS


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if _is_no_question(req.question):
        raise HTTPException(status_code=400, detail="question is required")
    try:
        answer, model_used = await get_completion(req.question)
        await push_message(req.question, answer, model_used, req.session_id)
        return AskResponse(answer=answer, model=model_used)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
