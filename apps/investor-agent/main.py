"""
Investor Agent: どの株を買うべきか等の投資相談に答える LLM Agent API
OpenAI 対応。必要に応じて Gemini 等のプロバイダを追加可能。
"""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

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


class AskRequest(BaseModel):
    question: str


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


@app.on_event("startup")
async def startup():
    if settings.openai_api_key:
        app.state.openai_client = get_openai_client()


@app.on_event("shutdown")
async def shutdown():
    if app.state.openai_client:
        await app.state.openai_client.close()


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "investor"}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    try:
        answer, model_used = await get_completion(req.question)
        return AskResponse(answer=answer, model=model_used)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
