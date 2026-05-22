#!/usr/bin/env bash
set -euo pipefail

docker compose up -d --build paraiba-hotdog-back

export API_AUTH_TOKEN
API_AUTH_TOKEN="$(scripts/keycloak-token.sh)"

poetry run pytest -m integration "$@"
