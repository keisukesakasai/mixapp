# mixapp

さまざまなアプリケーションをまとめるリポジトリです。

## 概要

このリポジトリでは、複数のアプリケーションやプロジェクトを管理していきます。

## アプリ

- **LLM アプリ** ([apps/llm-app/](apps/llm-app/)) — 質問を投げると LLM が答える HTTP API（OpenAI API 使用）
- **Load generator** ([apps/load-generator/](apps/load-generator/)) — LLM アプリへ質問を送り続ける負荷用クライアント

## インフラ

- **EKS**: [infra/eks/](infra/eks/) — AWS EKS クラスター（eksctl）。LLM アプリ・負荷試験用。
- **Kubernetes マニフェスト**: [infra/k8s/](infra/k8s/) — LLM アプリ・Load generator の Deployment/Service。イメージは `ghcr.io/keisukesakasai/mixapp-llm-app` と `ghcr.io/keisukesakasai/mixapp-load-generator`（GitHub Actions でビルド・プッシュ）。

## ライセンス

MIT
