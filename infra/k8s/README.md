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

### 手元で docker push するための準備（PAT）

1. GitHub → Settings → Developer settings → Personal access tokens で **Fine-grained** または **Classic** トークンを作成する。
2. **Classic** の場合: `write:packages`, `read:packages` にチェック。
3. **Fine-grained** の場合: 対象リポジトリ（または All repositories）で Permission: Packages を **Read and write** に設定。
4. トークンをコピーし、手元で環境変数に設定:
   ```bash
   export GITHUB_TOKEN=ghp_xxxx
   export GITHUB_USERNAME=keisukesakasai   # リポジトリオーナー。省略時は git remote から自動取得
   ```

### 方法 A: スクリプトでビルド・プッシュ・検証（推奨）

リポジトリルートで実行。プッシュ後に同じタグで `docker pull` して成功すれば push が有効であることを検証できます。

```bash
chmod +x scripts/docker-push-ghcr.sh

# 1 つのアプリだけ（検証用: chat-ui が軽い）
./scripts/docker-push-ghcr.sh chat-ui

# 全アプリをビルド・プッシュ
./scripts/docker-push-ghcr.sh all
```

### 方法 B: 手動でビルド・プッシュ

リポジトリルートで:

```bash
# GHCR へのログイン（上記 PAT を GITHUB_TOKEN に設定済みとする）
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

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

**検証**: どちらかの方法で push 後、別ターミナルで `docker pull ghcr.io/keisukesakasai/mixapp-chat-ui:latest` が成功すれば push は有効です。

## Secret の作成

Investor Agent は OpenAI API キーを必要とします。Datadog 観測（APM / LLM Observability）を使う場合は **Datadog API キー**も必要です。デプロイ前に Secret を作成してください。

```bash
kubectl create namespace mixapp --dry-run=client -o yaml | kubectl apply -f -

# OpenAI（必須）
kubectl create secret generic investor-agent-openai -n mixapp \
  --from-literal=openai-api-key=sk-your-openai-api-key

# Datadog（APM / LLM Observability 用。観測する場合は必須）
kubectl create secret generic datadog-secret -n mixapp \
  --from-literal=api-key=your-datadog-api-key
```

**API キーを .env に置く場合**: リポジトリルートの `.env` に `DD_API_KEY=あなたのキー` を追加しておくと（このファイルは .gitignore で Git に含まれない）、次のコマンドで Secret を作成・更新できる。

```bash
# リポジトリルートで
source .env
kubectl create secret generic datadog-secret -n mixapp \
  --from-literal=api-key="$DD_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

続けて Agent を再起動して新しいキーを読み込ませる: `kubectl rollout restart daemonset/datadog-agent -n mixapp`

Datadog API キーは [Datadog Organization Settings > API Keys](https://app.datadoghq.com/organization-settings/api-keys) で取得できます。

## Datadog Agent のデプロイ（観測を行う場合）

LLM アプリ（Investor Agent）のトレース・LLM Observability を Datadog で見るには、クラスターに Datadog Agent を入れます。**Datadog Operator** を使う方法（推奨）です。

**Kubernetes Explore**（Pods / Deployments 等のオーケストレーターリソース表示）を使う場合は、Datadog Agent >= v7.33.0 と Cluster Agent >= v1.18.0 が必要です。Operator v1.0.0+ はデフォルトで Cluster Agent をデプロイし、`datadog-agent.yaml` で `orchestratorExplorer.enabled: true` を設定済みです。

1. **Helm で Datadog Operator をインストール**（クラスターに 1 回だけ）

   ```bash
   helm repo add datadog https://helm.datadoghq.com
   helm install datadog-operator datadog/datadog-operator
   ```

2. **上記「Secret の作成」で `datadog-secret` を mixapp 名前空間に作成済みであること**

3. **Datadog Agent を適用**

   ```bash
   kubectl apply -f infra/k8s/datadog-agent.yaml
   ```

4. **確認**: Agent の DaemonSet が各ノードで動いていること

   ```bash
   kubectl get daemonset -n mixapp
   ```

`datadog-agent.yaml` の `spec.global.site` はリージョンに合わせて変更できます（例: 日本リージョンは `ap1.datadoghq.com`）。`spec.global.clusterName` は任意のクラスター名です。

## デプロイ

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/redis-deployment.yaml
# Datadog 観測を行う場合（上記手順で Secret 作成済みなら）
kubectl apply -f infra/k8s/datadog-agent.yaml
kubectl apply -f infra/k8s/investor-agent-deployment.yaml
kubectl apply -f infra/k8s/load-generator-deployment.yaml
kubectl apply -f infra/k8s/chat-ui-deployment.yaml
```

### イメージ更新後の反映（コード変更後）

Git push で GitHub Actions がイメージをビルド・GHCR に push したあと、以下で新しい Pod に切り替える。

```bash
kubectl rollout restart deploy/load-generator -n mixapp
# 必要に応じて
kubectl rollout restart deploy/investor-agent -n mixapp
kubectl rollout restart deploy/chat-ui -n mixapp
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
kubectl delete -f infra/k8s/datadog-agent.yaml   # Datadog を入れた場合
kubectl delete -f infra/k8s/redis-deployment.yaml
kubectl delete -f infra/k8s/namespace.yaml
```

Datadog Operator 自体を削除する場合: `helm uninstall datadog-operator`
