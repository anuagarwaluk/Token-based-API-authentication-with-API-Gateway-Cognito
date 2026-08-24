#!/usr/bin/env bash
# Create a confirmed test user with a permanent password.
# Usage: ./create_user.sh <user-pool-id> <email> <password> [region]
set -euo pipefail

POOL_ID="${1:?user pool id}"
USERNAME="${2:?email}"
PASSWORD="${3:?password}"
REGION="${4:-us-east-1}"

aws cognito-idp admin-create-user \
  --user-pool-id "$POOL_ID" \
  --username "$USERNAME" \
  --user-attributes Name=email,Value="$USERNAME" Name=email_verified,Value=true \
  --message-action SUPPRESS \
  --region "$REGION"

aws cognito-idp admin-set-user-password \
  --user-pool-id "$POOL_ID" \
  --username "$USERNAME" \
  --password "$PASSWORD" \
  --permanent \
  --region "$REGION"

echo "User $USERNAME created and confirmed."
