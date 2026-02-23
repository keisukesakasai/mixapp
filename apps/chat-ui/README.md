# Chat UI

Redis にスタックされた Investor Agent とのやりとり（質問・回答）を**参照して表示するだけ**の Web 画面です。送信フォームはなく、Load generator や API 経由で積まれた履歴を表示します。

## 機能

- **セッション単位**でやりとりを表示。ヘッダーのセッション選択で切り替え
- `GET /api/sessions` でセッション一覧、`GET /api/messages?session_id=xxx` でそのセッションの履歴を取得
- 更新ボタンと 10 秒ごとの自動更新

## 環境変数

| 変数 | 既定値 | 説明 |
|------|--------|------|
| REDIS_URL | redis://redis:6379/0 | Redis の URL |

## ローカル実行

```bash
cd apps/chat-ui
pip install -r requirements.txt
export REDIS_URL=redis://localhost:6379/0   # Redis を起動しておく
uvicorn main:app --reload --port 8080
```

ブラウザで http://localhost:8080 を開く。

## K8s デプロイ後

`chat-ui` の Service が LoadBalancer の場合、`kubectl get svc -n mixapp` の EXTERNAL-IP でアクセス可能（ポート 80）。
