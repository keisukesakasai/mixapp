# EKS セットアップ (mixapp)

## 使うアカウント・認証

- **AWS アカウント**: Datadog - mcse-sandbox（ID: `369042512949`、エイリアス: dd-mcse-sandbox）
- **認証**: `AWS_PROFILE=dd-mcse-sandbox` で SSO ロール（account-admin）を使用
- **リージョン**: `cluster.yaml` の `metadata.region`（`ap-northeast-1`）
- **名前プレフィックス**: クラスター・ノードグループとも `sakasai-` を付与

## 必要な権限

EKS クラスター作成には、IAM で以下に相当する権限が必要です。

- `AmazonEKSClusterPolicy`
- `AmazonEKSWorkerNodePolicy`（ノード用）
- `AmazonEC2ContainerRegistryReadOnly`
- EC2（VPC / サブネット / セキュリティグループ / キーペア等）、EKS、IAM の作成・更新・削除

マネコンから「EKS のクラスター作成」で進めると、必要なポリシーをまとめて付与しやすいです。

## クラスター作成

```bash
# mcse-sandbox で SSO ログイン済みであること: aws sso login --profile dd-mcse-sandbox
export AWS_PROFILE=dd-mcse-sandbox
eksctl create cluster -f infra/eks/cluster.yaml
```

所要時間はおおよそ 15〜20 分です。

## 作成後の確認

```bash
kubectl get nodes
kubectl get ns
```

## クラスターのアップグレード（1.31 → 1.35）

EKS は 1 マイナーずつしか上げられない。順に実行する:

```bash
export AWS_PROFILE=dd-mcse-sandbox
# 現在のバージョン確認
aws eks describe-cluster --name sakasai-mixapp-eks --region ap-northeast-1 --query 'cluster.version'

# 各ステップ（完了するたびに次を実行）
eksctl upgrade cluster --name sakasai-mixapp-eks --region ap-northeast-1 --version=1.32 --approve
eksctl upgrade cluster --name sakasai-mixapp-eks --region ap-northeast-1 --version=1.33 --approve
eksctl upgrade cluster --name sakasai-mixapp-eks --region ap-northeast-1 --version=1.34 --approve
eksctl upgrade cluster --name sakasai-mixapp-eks --region ap-northeast-1 --version=1.35 --approve

# コントロールプレーンが 1.35 になったらノードグループを更新
eksctl upgrade nodegroup --config-file infra/eks/cluster.yaml --name sakasai-ng-default
```

または `infra/eks/upgrade-to-135.sh` を繰り返し実行（現在のバージョンに応じて次の 1 段階だけ実行）。

## クラスター削除

```bash
eksctl delete cluster -f infra/eks/cluster.yaml
```
