# IntelliTrack Security Documentation

## 1. Purpose

This document records the security controls implemented in IntelliTrack and how those controls are validated before release.

## 2. Threat Model Summary

Main attack surfaces:

1. public web/API endpoints
2. authentication/token boundary
3. service-to-service communication
4. data store access and secret handling

Primary risks addressed:

- unauthorized access
- credential compromise
- brute-force attempts on login
- injection attacks
- cloud network misconfiguration

## 3. Implemented Controls

### 3.1 Authentication and authorization

- JWT bearer authentication for protected APIs
- role-based access checks via dependency injection
- invalid token requests fail with `401`
- insufficient role requests fail with `403`

Reference implementation:

- `app/auth.py`
- protected endpoints in `app/main.py`

### 3.2 Password security

- PBKDF2-HMAC-SHA256
- 100,000 iterations
- unique random salt per password
- no plaintext storage

### 3.3 API hardening

- schema validation through Pydantic
- SQLAlchemy ORM (parameterized access pattern)
- rate limiting with `slowapi` on auth paths
- security headers middleware (nosniff, frame deny, HSTS, policy headers)
- CORS allowlist via `ALLOWED_ORIGINS`

### 3.4 Secret management

- required `SECRET_KEY` enforced at startup
- runtime secrets expected via environment/secret manager
- no production secret values in repository source

### 3.5 Cloud/network controls

- private service connectivity through ECS/Service Connect
- controlled ingress through ALB and security groups
- CloudWatch logging for investigation and audit trails

## 4. Security Validation Process

Validation activities:

1. auth-negative tests (`401` and `403` paths)
2. rate-limit verification (`429` on threshold)
3. OWASP ZAP quick scan of API surface
4. manual review of high-risk endpoints

Sample scan command:

```bash
zap-cli quick-scan http://127.0.0.1:8000
```

## 5. Secure Development Practices

Practices followed:

- validate all external input at API boundary
- keep auth logic centralized in `app/auth.py`
- separate business logic, persistence, and transport concerns
- avoid dynamic SQL string construction
- use least-privilege cloud roles and scoped connectivity

## 6. Incident Readiness (Current)

Operational controls in place:

- CloudWatch logs for runtime error/auth anomaly review
- ECS health checks for automatic unhealthy task replacement
- credential rotation supported through environment/secret updates

## 7. Release Security Checklist

Before release:

1. `SECRET_KEY` and runtime secrets verified
2. auth/role tests pass on critical routes
3. no unresolved high-severity findings in security scan
4. rate limiting confirmed on login/register flows
5. CORS origin configuration verified

## 8. Residual Risks and Next Steps

Recommended improvements:

1. add automated SAST/DAST in CI gate
2. add anomaly alerts for suspicious auth traffic
3. codify security policy checks for IaC/runtime drift
