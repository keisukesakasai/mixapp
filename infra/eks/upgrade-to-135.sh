#!/usr/bin/env bash
# EKS コントロールプレーンを 1.31 → 1.35 に段階的にアップグレードするスクリプト
# 各ステップ完了後に次のコマンドを実行（1 マイナーずつしか上げられない）
set -e
export AWS_PROFILE=${AWS_PROFILE:-dd-mcse-sandbox}
CLUSTER=sakasai-mixapp-eks
REGION=ap-northeast-1

CURRENT=$(aws eks describe-cluster --name "$CLUSTER" --region "$REGION" --query 'cluster.version' --output text)
echo "Current cluster version: $CURRENT"

upgrade_one() {
  local from=$1
  local to=$2
  echo "Upgrading control plane $from → $to ..."
  eksctl upgrade cluster --name "$CLUSTER" --region "$REGION" --version="$to" --approve
  echo "Control plane is now $to."
}

# 現在のバージョンに応じて必要なアップグレードだけ実行
case "$CURRENT" in
  1.31) upgrade_one 1.31 1.32 ;;
  1.32) upgrade_one 1.32 1.33 ;;
  1.33) upgrade_one 1.33 1.34 ;;
  1.34) upgrade_one 1.34 1.35 ;;
  1.35) echo "Already on 1.35. Upgrading nodegroup if needed." ;;
  *)    echo "Unexpected version: $CURRENT"; exit 1 ;;
esac

# 1.35 になったらノードグループを更新（新しいノードが 1.35 で起動するようになる）
if [[ "$(aws eks describe-cluster --name "$CLUSTER" --region "$REGION" --query 'cluster.version' --output text)" == "1.35" ]]; then
  echo "Upgrading nodegroup to 1.35..."
  SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
  eksctl upgrade nodegroup --config-file "$SCRIPT_DIR/cluster.yaml" --name sakasai-ng-default
fi

echo "Done. Check: aws eks describe-cluster --name $CLUSTER --region $REGION --query 'cluster.version'"
