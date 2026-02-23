"""
LLM アプリ: 質問を受け取り LLM で回答する HTTP API
"""
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str | None = None  # カスタムエンドポイント用
    model: str = "gpt-4o-mini"
    port: int = 8000


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    model: str


def get_client() -> AsyncOpenAI:
    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return AsyncOpenAI(**kwargs)


settings = Settings()
app = FastAPI(title="mixapp-llm")
app.state.client = None


@app.on_event("startup")
async def startup():
    if settings.openai_api_key:
        app.state.client = get_client()


@app.on_event("shutdown")
async def shutdown():
    if app.state.client:
        await app.state.client.close()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    if not app.state.client:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
    try:
        completion = await app.state.client.chat.completions.create(
            model=settings.model,
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。簡潔に答えてください。"},
                {"role": "user", "content": req.question},
            ],
            max_tokens=512,
        )
        answer = completion.choices[0].message.content or ""
        return AskResponse(answer=answer, model=completion.model)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
