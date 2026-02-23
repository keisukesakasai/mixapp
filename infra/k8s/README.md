# Kubernetes マニフェスト (mixapp)

LLM アプリと Load generator を EKS にデプロイするためのマニフェストです。

## 前提

- EKS クラスターが作成済み（[infra/eks/](../eks/) を参照）
- `kubectl` でクラスターに接続済み
- イメージは **main ブランチへの push で GitHub Actions が自動ビルド・GHCR へプッシュ**します（[.github/workflows/build-push-images.yaml](../../.github/workflows/build-push-images.yaml)）。手動でビルドする場合は下記「イメージのビルドとプッシュ」を参照。

## イメージのビルドとプッシュ

リポジトリルートで:

```bash
# GHCR へのログイン（公開イメージの push には PAT が必要）
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# LLM アプリ
docker build -t ghcr.io/keisukesakasai/mixapp-llm-app:latest apps/llm-app
docker push ghcr.io/keisukesakasai/mixapp-llm-app:latest

# Load generator
docker build -t ghcr.io/keisukesakasai/mixapp-load-generator:latest apps/load-generator
docker push ghcr.io/keisukesakasai/mixapp-load-generator:latest
```

## Secret の作成

LLM アプリは OpenAI API キーを必要とします。デプロイ前に Secret を作成してください。

```bash
kubectl create namespace mixapp --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic llm-app-openai -n mixapp \
  --from-literal=openai-api-key=sk-your-openai-api-key
```

## デプロイ

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/llm-app-deployment.yaml
kubectl apply -f infra/k8s/load-generator-deployment.yaml
```

## 確認

```bash
kubectl get pods -n mixapp
kubectl get svc -n mixapp
kubectl logs -n mixapp -l app=load-generator -f
```

## 削除

```bash
kubectl delete -f infra/k8s/load-generator-deployment.yaml
kubectl delete -f infra/k8s/llm-app-deployment.yaml
kubectl delete -f infra/k8s/namespace.yaml
```
