# Chat UI

Investor Agent とのやりとり（質問と回答）が見える Web チャット画面です。

## 機能

- 画面上で質問を入力して送信すると、Investor Agent が回答を返します
- やりとりの履歴がその場に表示されます（あなた / Investor Agent の吹き出し）

## 環境変数

| 変数 | 既定値 | 説明 |
|------|--------|------|
| INVESTOR_AGENT_URL | http://investor-agent:8000 | Investor Agent の URL |

## ローカル実行

```bash
cd apps/chat-ui
pip install -r requirements.txt
export INVESTOR_AGENT_URL=http://localhost:8000   # Investor Agent を別ターミナルで起動しておく
uvicorn main:app --reload --port 8080
```

ブラウザで http://localhost:8080 を開く。

## K8s デプロイ後

`chat-ui` の Service が LoadBalancer の場合、`kubectl get svc -n mixapp` の EXTERNAL-IP でアクセス可能（ポート 80）。

イメージがまだ GHCR にない場合は、main に push して GitHub Actions でビルドするか、手動で `docker build` / `docker push` してください。
