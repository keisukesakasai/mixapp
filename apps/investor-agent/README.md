# Investor Agent

「どの株を今買うべきか」などの投資相談に答える LLM Agent API です。  
現在は OpenAI 対応。**各応答は Redis にスタックされ、Chat UI がそれを参照する。**

## 環境変数

| 変数 | 必須 | 説明 |
|------|------|------|
| OPENAI_API_KEY | ○ | OpenAI API キー |
| OPENAI_BASE_URL | - | カスタムエンドポイント（省略時は OpenAI 本番） |
| MODEL | - | モデル名（既定: gpt-4o-mini） |
| PORT | - | 待ち受けポート（既定: 8000） |
| REDIS_URL | redis://redis:6379/0 | やりとりをスタックする Redis の URL |

## ローカル実行

リポジトリルートに `.env` を置き `OPENAI_API_KEY=sk-xxx` を書いておくと、起動時に自動で読まれる（`.env` は Git に含めない想定。テンプレは `.env.example`）。

```bash
cd apps/investor-agent
pip install -r requirements.txt
# OPENAI_API_KEY は .env に書くか、ここで export してもよい
uvicorn main:app --reload --port 8000
```

## API

- `GET /health` — ヘルスチェック（`agent: investor` を返す）
- `POST /ask` — 投資相談の質問を送り回答を得る。応答は Redis にセッション別で積まれる。  
  Body: `{"question": "今買うべき株を3つ教えて", "session_id": "optional"}` → `{"answer": "...", "model": "..."}`  
  `session_id` を省略すると `"default"` として記録される。

回答には「投資助言ではありません」の注意書きが含まれます。
