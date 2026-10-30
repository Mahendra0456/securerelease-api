#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

NEW_TAG="${1:-}"

if [[ ! "$NEW_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Usage: ./scripts/release.sh v1.0.0"
    exit 1
fi

STATE_FILE=".release-state"
CURRENT_TAG="local"
PREVIOUS_TAG=""

if [[ -f "$STATE_FILE" ]]; then
    read -r CURRENT_TAG PREVIOUS_TAG < "$STATE_FILE"
fi

echo "Previous release: $CURRENT_TAG"
echo "Deploying release: $NEW_TAG"

export TAG="$NEW_TAG"

docker compose build api
docker compose up -d --no-build api

echo "Waiting for API health check..."

HEALTHY=false

for i in {1..30}; do
    if curl -fsS http://127.0.0.1:8000/health; then
        HEALTHY=true
        break
    fi
    sleep 2
done

if [[ "$HEALTHY" != "true" ]]; then
    echo "Release failed. Restoring $CURRENT_TAG"

    export TAG="$CURRENT_TAG"
    docker compose up -d --no-build api

    exit 1
fi

printf '%s %s\n' "$NEW_TAG" "$CURRENT_TAG" > "$STATE_FILE"

echo
echo "Release successful: $NEW_TAG"
