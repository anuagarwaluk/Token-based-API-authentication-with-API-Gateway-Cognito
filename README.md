# Token-based API authentication with API Gateway + Cognito

A REST API on Amazon API Gateway protected by a Cognito User Pool authorizer. Every request is verified at the gateway: signature, expiry, issuer and audience, checked against the pool's public keys before Lambda runs. The function receives pre-verified identity claims and never touches a JWT.

<img width="2400" height="3000" alt="architectureapigwcognito" src="https://github.com/user-attachments/assets/e56bfc57-bf37-4381-904f-9027f88d6cb2" />


## How it works

1. The client signs in to Cognito once (`USER_PASSWORD_AUTH`) and receives a signed JWT.
2. Every API call carries the token in the `Authorization` header.
3. The Cognito authorizer on API Gateway validates the token against the pool's JWKS. Invalid or missing token: `401` at the gateway, Lambda never runs.
4. Valid token: API Gateway injects the verified claims into `event.requestContext.authorizer.claims` and invokes Lambda.

The result is stateless authentication with no session store, no auth code in the application, and a single place to audit enforcement.

## Repository layout

```
├── src/            Lambda handler (Python 3.11)
├── infra/          SAM template: user pool, app client, API, authorizer, function
├── scripts/        Create a test user, fetch a JWT, run the 401/200 test
├── tests/          Unit tests for the handler (pytest)
└── docs/           Architecture diagram, setup guide, design decisions
```

## Quick start

```bash
# Deploy
cd infra && sam build && sam deploy --guided

# Create a confirmed test user
./scripts/create_user.sh <user-pool-id> you@example.com '<StrongPassword1!>'

# Get a token and test both paths
TOKEN=$(./scripts/get_token.sh <app-client-id> you@example.com '<StrongPassword1!>')
./scripts/test_api.sh <api-endpoint> "$TOKEN"
```

Expected: `HTTP 401` without the token, `HTTP 200` with it, and a JSON body showing `"authenticated": true` with the caller's identity.

## Key lessons

- **Authentication as configuration.** One authorizer on the method request protects every route. Nothing to patch in application code.
- **Rejected requests are free.** A bad token is refused at the gateway. No Lambda invocation, no cost, no attack surface.
- **Deploy the stage.** Authorizer changes do nothing until the API is redeployed. Verify the 401 before trusting the setup.
- **ID token vs access token.** Without OAuth scopes the authorizer accepts the ID token; with scopes, only the access token passes.
- **Know when to use the ALB pattern instead.** Cookie-based auth at the load balancer suits browser apps; token-based auth at the gateway suits mobile, SPAs and service-to-service calls. See [docs/design-decisions.md](docs/design-decisions.md).


*Built and measured by Anu Agarwal — [linkedin.com/in/agarwalanu](https://www.linkedin.com/in/agarwalanu)*

<img width="732" height="56" alt="image" src="https://github.com/user-attachments/assets/6d6d2775-4fcf-45af-a872-aa3b19b7db72" />
