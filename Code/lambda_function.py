"""Hello World Lambda behind API Gateway with a Cognito User Pool authorizer.

API Gateway validates the JWT before this function runs, so the code never
parses a token. If the request was authenticated, the verified claims arrive
in event.requestContext.authorizer.claims.
"""

import json
import os


def extract_cognito_user(event):
    """Return verified Cognito claims injected by the API Gateway authorizer."""
    authorizer = event.get("requestContext", {}).get("authorizer", {})
    claims = authorizer.get("claims")
    if not claims:
        return None
    return {
        "username": claims.get("cognito:username", "Unknown"),
        "email": claims.get("email", "Unknown"),
        "sub": claims.get("sub", "Unknown"),
        "token_use": claims.get("token_use", "Unknown"),
    }


def lambda_handler(event, context):
    env = os.environ.get("ENVIRONMENT", "unknown")

    method = event.get("httpMethod", "UNKNOWN")
    path = event.get("path", "/")
    headers = event.get("headers", {})
    query_params = event.get("queryStringParameters") or {}
    request_context = event.get("requestContext", {})

    cognito_user = extract_cognito_user(event)

    response_body = {
        "message": "Hello World from Lambda with API Gateway and Cognito Authentication!",
        "environment": env,
        "authentication": {
            "authenticated": cognito_user is not None,
            "user_info": cognito_user or "No authentication information available",
        },
        "request_info": {
            "method": method,
            "path": path,
            "query_parameters": query_params,
            "user_agent": headers.get("User-Agent", "Unknown"),
            "protocol": headers.get("X-Forwarded-Proto", "Unknown"),
        },
        "lambda_info": {
            "function_name": context.function_name,
            "function_version": context.function_version,
            "aws_request_id": context.aws_request_id,
        },
        "api_gateway_info": {
            "request_id": request_context.get("requestId", "Unknown"),
            "stage": request_context.get("stage", "Unknown"),
            "api_id": request_context.get("apiId", "Unknown"),
        },
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            # Demo-friendly CORS. Lock Allow-Origin down to your web origin
            # in production.
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "86400",
        },
        "body": json.dumps(response_body, indent=2),
    }
