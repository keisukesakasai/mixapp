# LLM アプリ

質問を受け取り OpenAI API で回答を返す HTTP API です。

## 環境変数

| 変数 | 必須 | 説明 |
|------|------|------|
| OPENAI_API_KEY | ○ | OpenAI API キー |
| OPENAI_BASE_URL | - | カスタムエンドポイント（省略時は OpenAI 本番） |
| MODEL | - | モデル名（既定: gpt-4o-mini） |
| PORT | - | 待ち受けポート（既定: 8000） |

## ローカル実行

```bash
cd apps/llm-app
pip install -r requirements.txt
export OPENAI_API_KEY=sk-xxx
uvicorn main:app --reload --port 8000
```

## API

- `GET /health` — ヘルスチェック
- `POST /ask` — 質問を送り回答を得る  
  Body: `{"question": "1+1は?"}` → `{"answer": "...", "model": "..."}`
