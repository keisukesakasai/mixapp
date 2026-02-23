#!/usr/bin/env bash
# .env を読み込んで GHCR に docker login する。一度実行すれば Docker に認証が保存され、以降 docker push が可能。
# リポジトリルートで実行: ./scripts/docker-login-ghcr.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  source "$REPO_ROOT/.env"
  set +a
fi

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Error: .env に GITHUB_TOKEN がありません。" >&2
  exit 1
fi

USER="${GITHUB_USERNAME:-}"
if [[ -z "$USER" ]]; then
  if origin=$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null); then
    if [[ "$origin" =~ github\.com[:/]([^/]+)/ ]]; then
      USER="${BASH_REMATCH[1]}"
    fi
  fi
fi
if [[ -z "$USER" ]]; then
  echo "Error: .env に GITHUB_USERNAME を設定するか、git remote から取得できるようにしてください。" >&2
  exit 1
fi

echo "Logging in to ghcr.io as $USER ..."
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$USER" --password-stdin
echo "Done. このターミナル以外でも docker push が使えます。"
