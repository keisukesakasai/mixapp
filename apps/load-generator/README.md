# Load generator (Investor Agent 用)

Investor Agent へ投資関連の質問を一定間隔で送り続ける負荷用クライアントです。  
あわせて **LLM Observability**（Datadog 等）の評価をトリガーするプロンプト（toxicity / sentiment / prompt-injection / failure-to-answer / sensitive-data）を混ぜて送信します。

## 環境変数

| 変数 | 既定値 | 説明 |
|------|--------|------|
| LLM_APP_URL | http://investor-agent:8000 | Investor Agent の URL |
| INTERVAL_SEC | 2.0 | 質問送信間隔（秒） |
| SESSION_ID | （自動生成） | セッション ID。未指定時は loadgen-{uuid} で 1 回だけ生成し、全リクエストで共通利用 |
| EVAL_PROMPT_RATIO | 0.65 | 有害・異常プロンプト（評価用）を送る割合（0.0〜1.0）。0 にすると通常の投資質問のみ |

## ローカル実行

```bash
cd apps/load-generator
pip install -r requirements.txt
export LLM_APP_URL=http://localhost:8000
python main.py
```

（先に Investor Agent を起動しておくこと）
