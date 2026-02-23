# Kubernetes マニフェスト (mixapp)

Investor Agent・Load generator・チャット UI・Redis を EKS にデプロイするためのマニフェストです。やりとりは Redis にスタックされ、UI は参照のみ。

## デプロイフロー（統一）

**Git push → GitHub Actions でビルド → GHCR へ push → 本マニフェストで `kubectl apply`** でデプロイする。Agent のイメージ一覧は [build-push-images.yaml](../../.github/workflows/build-push-images.yaml) の `matrix.app` で定義されている。新規 Agent 追加時は `.cursor/rules/deployment.mdc` のチェックリストに従うこと。

## 前提

- EKS クラスターが作成済み（[infra/eks/](../eks/) を参照）
- `kubectl` でクラスターに接続済み
- イメージは **main ブランチへの push で GitHub Actions が自動ビルド・GHCR へプッシュ**します（[.github/workflows/build-push-images.yaml](../../.github/workflows/build-push-images.yaml)）。手動でビルドする場合は下記「イメージのビルドとプッシュ」を参照。
- **CI デプロイ**: 上記ワークフローはビルド後に EKS へ自動デプロイします。リポジトリの GitHub Secrets に `AWS_ACCESS_KEY_ID` と `AWS_SECRET_ACCESS_KEY`（EKS クラスターにアクセスできる IAM ユーザー）を登録してください。

## イメージのビルドとプッシュ

リポジトリルートで:

```bash
# GHCR へのログイン（公開イメージの push には PAT が必要）
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Investor Agent
docker build -t ghcr.io/keisukesakasai/mixapp-investor-agent:latest apps/investor-agent
docker push ghcr.io/keisukesakasai/mixapp-investor-agent:latest

# Load generator
docker build -t ghcr.io/keisukesakasai/mixapp-load-generator:latest apps/load-generator
docker push ghcr.io/keisukesakasai/mixapp-load-generator:latest

# Chat UI
docker build -t ghcr.io/keisukesakasai/mixapp-chat-ui:latest apps/chat-ui
docker push ghcr.io/keisukesakasai/mixapp-chat-ui:latest
```

## Secret の作成

Investor Agent は OpenAI API キーを必要とします。デプロイ前に Secret を作成してください。

```bash
kubectl create namespace mixapp --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic investor-agent-openai -n mixapp \
  --from-literal=openai-api-key=sk-your-openai-api-key
```

## デプロイ

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/redis-deployment.yaml
kubectl apply -f infra/k8s/investor-agent-deployment.yaml
kubectl apply -f infra/k8s/load-generator-deployment.yaml
kubectl apply -f infra/k8s/chat-ui-deployment.yaml
```

## 確認

```bash
kubectl get pods -n mixapp
kubectl get svc -n mixapp
kubectl logs -n mixapp -l app=load-generator -f
```

**チャット UI**: Service が LoadBalancer なので、`kubectl get svc chat-ui -n mixapp` の EXTERNAL-IP にブラウザで http://EXTERNAL-IP でアクセスできる（イメージが pull できていれば）。

## 削除

```bash
kubectl delete -f infra/k8s/chat-ui-deployment.yaml
kubectl delete -f infra/k8s/load-generator-deployment.yaml
kubectl delete -f infra/k8s/investor-agent-deployment.yaml
kubectl delete -f infra/k8s/redis-deployment.yaml
kubectl delete -f infra/k8s/namespace.yaml
```
