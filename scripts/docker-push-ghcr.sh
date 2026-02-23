#!/usr/bin/env bash
# 手元から GHCR へ Docker イメージをビルド・プッシュし、検証するスクリプト
# 使い方:
#   export GITHUB_TOKEN=ghp_xxxx   # PAT (write:packages, read:packages)
#   export GITHUB_USERNAME=keisukesakasai  # 省略時は git remote から取得を試行
#   ./scripts/docker-push-ghcr.sh [app-name]   # 省略時は chat-ui で検証用に 1 つだけ
#   ./scripts/docker-push-ghcr.sh all          # 全アプリをビルド・プッシュ
# 検証: プッシュ後に同じタグで pull して成功すれば push 成功とみなす

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${GITHUB_TOKEN:-}" && -f "$REPO_ROOT/.env" ]]; then
  set -a
  source "$REPO_ROOT/.env"
  set +a
fi

REGISTRY="ghcr.io"
REPO_OWNER="${GITHUB_USERNAME:-}"
APPS=(investor-agent load-generator chat-ui)

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Error: GITHUB_TOKEN が未設定です。GitHub PAT (write:packages, read:packages) を設定してください。" >&2
  echo "  export GITHUB_TOKEN=ghp_xxxx" >&2
  exit 1
fi

if [[ -z "$REPO_OWNER" ]]; then
  if origin=$(git remote get-url origin 2>/dev/null); then
    if [[ "$origin" =~ github\.com[:/]([^/]+)/ ]]; then
      REPO_OWNER="${BASH_REMATCH[1]}"
    fi
  fi
  if [[ -z "$REPO_OWNER" ]]; then
    echo "Error: GITHUB_USERNAME が未設定で、git remote からも取得できません。export GITHUB_USERNAME=your-username を設定してください。" >&2
    exit 1
  fi
  echo "Using repository owner: $REPO_OWNER (from git remote)"
fi

echo "Logging in to $REGISTRY as $REPO_OWNER ..."
echo "$GITHUB_TOKEN" | docker login "$REGISTRY" -u "$REPO_OWNER" --password-stdin

# EKS ノードは x86_64。Mac ARM でビルドすると arm64 になり exec format error になるため --platform 必須
PLATFORM="${DOCKER_PLATFORM:-linux/amd64}"

build_push_one() {
  local app="$1"
  local tag="${REGISTRY}/${REPO_OWNER}/mixapp-${app}:latest"
  echo "--- Build and push: $app (platform=$PLATFORM) ---"
  docker build --platform "$PLATFORM" -t "$tag" "apps/$app"
  docker push "$tag"
  echo "Verify: pull same image ..."
  docker pull "$tag"
  echo "OK: $tag の push と pull の検証が完了しました。"
}

TARGET="${1:-chat-ui}"
if [[ "$TARGET" == "all" ]]; then
  for app in "${APPS[@]}"; do
    build_push_one "$app"
  done
else
  if [[ ! -d "apps/$TARGET" ]]; then
    echo "Error: apps/$TARGET が存在しません。app は次のいずれか: ${APPS[*]}, all" >&2
    exit 1
  fi
  build_push_one "$TARGET"
fi
