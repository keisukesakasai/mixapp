# mixapp

さまざまなアプリケーションをまとめるリポジトリです。

## 概要

このリポジトリでは、複数のアプリケーションやプロジェクトを管理していきます。

## アプリ

- **Investor Agent** ([apps/investor-agent/](apps/investor-agent/)) — 「どの株を買うべきか」等の投資相談に答える LLM Agent API（OpenAI 対応、Gemini 等の追加可能）
- **Load generator** ([apps/load-generator/](apps/load-generator/)) — Investor Agent へ投資関連の質問を送り続ける負荷用クライアント
- **Chat UI** ([apps/chat-ui/](apps/chat-ui/)) — やりとりが見える Web チャット画面（Investor Agent に質問して回答を表示）

## インフラ

- **EKS**: [infra/eks/](infra/eks/) — AWS EKS クラスター（eksctl）。LLM アプリ・負荷試験用。
- **Kubernetes マニフェスト**: [infra/k8s/](infra/k8s/) — Investor Agent・Load generator の Deployment/Service。イメージは `ghcr.io/keisukesakasai/mixapp-investor-agent` と `ghcr.io/keisukesakasai/mixapp-load-generator`（GitHub Actions でビルド・プッシュ）。

## ライセンス

MIT
