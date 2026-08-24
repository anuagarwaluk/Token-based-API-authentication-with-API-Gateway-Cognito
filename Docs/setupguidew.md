# Setup guide

Two ways to build this: deploy the SAM template, or configure it in the console. Both end at the same test.

## Option A: Deploy with SAM

```bash
cd infra
sam build
sam deploy --guided
```

Note the three outputs: `ApiEndpoint`, `UserPoolId`, `AppClientId`.

## Option B: Console walkthrough

1. **User pool.** Cognito → Create user pool → Single page application. Sign-in identifier: email. Required attribute: email. No client secret: API Gateway authorizers expect bare JWTs, and a public client cannot protect a secret anyway.
2. **Test user.** Create a user with a verified email, then set a permanent password (or use `scripts/create_user.sh`).
3. **Authorizer.** API Gateway → your API → Authorizers → Create. Type: Cognito. Pool: the one above. Token source: `Authorization`.
4. **Protect the methods.** Resources → `ANY /` → Method Request → Authorization: your authorizer. Repeat for `ANY /{proxy+}`.
5. **Deploy the stage.** Deploy API → `prod`. Nothing takes effect until this step.
6. **Enable the auth flow.** User pool → App clients → your client → enable `ALLOW_USER_PASSWORD_AUTH`.

## Test it

```bash
# 401 without a token
curl -i https://<api-id>.execute-api.<region>.amazonaws.com/prod

# Get a JWT
./scripts/get_token.sh <app-client-id> <email> '<password>'

# 200 with the token, response shows "authenticated": true
./scripts/test_api.sh <api-endpoint> <id-token>
```

## Gotchas worth knowing

- **Un-deployed changes.** Attaching an authorizer changes nothing until the stage is redeployed. Test the 401 first.
- **ID token vs access token.** With no OAuth scopes on the method, send the ID token. With scopes configured, only the access token passes.
- **Authorizer caching.** Results are cached (default 300 seconds) keyed on the token, so a just-revoked token can pass until the cache entry expires.
