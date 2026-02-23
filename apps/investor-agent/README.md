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
| DD_API_KEY | 観測時 | Datadog API キー（APM / LLM Observability 用）。K8s では Secret `datadog-secret` から渡す。 |
| DD_LLMOBS_ENABLED | - | `1` で LLM Observability を有効化（K8s ではデプロイ側で設定済み） |
| DD_AGENT_HOST | - | トレース送信先の Datadog Agent ホスト。K8s では同一ノードの Agent に自動設定。 |
| DD_ENV | - | 環境タグ（例: `staging`）。Datadog で env で絞り込む用。K8s では `staging` を設定済み。 |

## ローカル実行

リポジトリルートに `.env` を置き `OPENAI_API_KEY=sk-xxx` を書いておくと、起動時に自動で読まれる（`.env` は Git に含めない想定。テンプレは `.env.example`）。

```bash
cd apps/investor-agent
pip install -r requirements.txt
# OPENAI_API_KEY は .env に書くか、ここで export してもよい
uvicorn main:app --reload --port 8000
```

Datadog でトレース・LLM Observability を見る場合は `ddtrace-run` で起動し、`DD_API_KEY` と `DD_LLMOBS_ENABLED=1` を設定する（`.env` に `DD_API_KEY=` を追加しても可）。

```bash
DD_LLMOBS_ENABLED=1 DD_API_KEY=your-datadog-api-key ddtrace-run uvicorn main:app --reload --port 8000
```

**LLM Observability の公式手順**: [Automatic Instrumentation for LLM Observability (Python)](https://docs.datadoghq.com/ja/llm_observability/instrumentation/auto_instrumentation?tab=python)。本アプリは OpenAI Python SDK の `chat.completions.create` を使用しており、ddtrace 2.9.0+ と `DD_LLMOBS_ENABLED=1` で自動計測されます。

## API

- `GET /health` — ヘルスチェック（`agent: investor` を返す）
- `POST /ask` — 投資相談の質問を送り回答を得る。応答は Redis にセッション別で積まれる。  
  Body: `{"question": "今買うべき株を3つ教えて", "session_id": "optional"}` → `{"answer": "...", "model": "..."}`  
  `session_id` を省略すると `"default"` として記録される。

回答には「投資助言ではありません」の注意書きが含まれます。
