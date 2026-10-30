#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

STATE_FILE=".release-state"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "No release history found. Nothing to roll back."
    exit 1
fi

read -r CURRENT_TAG PREVIOUS_TAG < "$STATE_FILE"

if [[ -z "${PREVIOUS_TAG:-}" ]]; then
    echo "No previous release available."
    exit 1
fi

if ! docker image inspect "apex-ops-api:$PREVIOUS_TAG" >/dev/null 2>&1; then
    echo "Previous image not found: apex-ops-api:$PREVIOUS_TAG"
    exit 1
fi

echo "Current release: $CURRENT_TAG"
echo "Rolling back to: $PREVIOUS_TAG"

export TAG="$PREVIOUS_TAG"
docker compose up -d --no-build api

echo "Checking API health..."

HEALTHY=false

for i in {1..30}; do
    if curl -fsS http://127.0.0.1:8000/health; then
        HEALTHY=true
        break
    fi
    sleep 2
done

if [[ "$HEALTHY" != "true" ]]; then
    echo "Rollback health check failed. Restoring $CURRENT_TAG"

    export TAG="$CURRENT_TAG"
    docker compose up -d --no-build api

    exit 1
fi

printf '%s %s\n' "$PREVIOUS_TAG" "$CURRENT_TAG" > "$STATE_FILE"

echo
echo "Rollback successful: $PREVIOUS_TAG"
