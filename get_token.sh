#!/usr/bin/env bash
# Obtain a Cognito JWT (ID token) with the USER_PASSWORD_AUTH flow.
# Usage: ./get_token.sh <app-client-id> <email> <password> [region]
set -euo pipefail

CLIENT_ID="${1:?app client id}"
USERNAME="${2:?email}"
PASSWORD="${3:?password}"
REGION="${4:-us-east-1}"

aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$CLIENT_ID" \
  --auth-parameters "USERNAME=$USERNAME,PASSWORD=$PASSWORD" \
  --region "$REGION" \
  --query 'AuthenticationResult.IdToken' \
  --output text
