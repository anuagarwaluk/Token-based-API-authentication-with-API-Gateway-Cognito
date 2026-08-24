#!/usr/bin/env bash
# Prove the authorizer works: expect 401 without a token, 200 with one.
# Usage: ./test_api.sh <api-endpoint> [id-token]
set -euo pipefail

API_ENDPOINT="${1:?api endpoint, e.g. https://abc123.execute-api.us-east-1.amazonaws.com/prod}"
TOKEN="${2:-}"

echo "--- 1. Unauthenticated request (expect 401) ---"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$API_ENDPOINT"

if [[ -n "$TOKEN" ]]; then
  echo "--- 2. Authenticated request (expect 200) ---"
  curl -s -w "\nHTTP %{http_code}\n" -H "Authorization: $TOKEN" "$API_ENDPOINT"
else
  echo "Pass an ID token as the second argument to run the authenticated test."
fi
