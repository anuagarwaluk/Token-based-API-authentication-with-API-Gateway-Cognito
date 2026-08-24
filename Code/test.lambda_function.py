"""Unit tests for the Lambda handler. Run with: python -m pytest tests/ -v"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lambda_function import lambda_handler  # noqa: E402

CONTEXT = SimpleNamespace(
    function_name="apigw-cognito-hello",
    function_version="$LATEST",
    aws_request_id="test-request-id",
)


def base_event(**overrides):
    event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {"User-Agent": "pytest", "X-Forwarded-Proto": "https"},
        "queryStringParameters": None,
        "requestContext": {"requestId": "r-1", "stage": "prod", "apiId": "abc123"},
    }
    event.update(overrides)
    return event


def test_unauthenticated_request():
    result = lambda_handler(base_event(), CONTEXT)
    body = json.loads(result["body"])
    assert result["statusCode"] == 200
    assert body["authentication"]["authenticated"] is False


def test_authenticated_request_exposes_claims():
    event = base_event()
    event["requestContext"]["authorizer"] = {
        "claims": {
            "cognito:username": "anu",
            "email": "user@example.com",
            "sub": "1234-5678",
            "token_use": "id",
        }
    }
    result = lambda_handler(event, CONTEXT)
    body = json.loads(result["body"])
    assert body["authentication"]["authenticated"] is True
    assert body["authentication"]["user_info"]["email"] == "user@example.com"
    assert body["authentication"]["user_info"]["token_use"] == "id"


def test_handles_missing_query_params():
    result = lambda_handler(base_event(queryStringParameters=None), CONTEXT)
    body = json.loads(result["body"])
    assert body["request_info"]["query_parameters"] == {}
