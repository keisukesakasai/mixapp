# Load generator (Investor Agent 用)

Investor Agent へ投資関連の質問を一定間隔で送り続ける負荷用クライアントです。

## 環境変数

| 変数 | 既定値 | 説明 |
|------|--------|------|
| LLM_APP_URL | http://investor-agent:8000 | Investor Agent の URL |
| INTERVAL_SEC | 2.0 | 質問送信間隔（秒） |

## ローカル実行

```bash
cd apps/load-generator
pip install -r requirements.txt
export LLM_APP_URL=http://localhost:8000
python main.py
```

（先に Investor Agent を起動しておくこと）
