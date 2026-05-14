# IntelliTrack Test Documentation

## 1. Purpose

This document defines the testing approach for IntelliTrack and provides reproducible commands for local and cloud-aligned verification.

## 2. Test Scope

Covered layers:

1. Backend API and business logic
2. Frontend component behavior
3. AI service endpoints and analysis flow
4. End-to-end functional paths
5. Performance and security checks

## 3. Test Locations

Important paths:

- backend tests: repository root (pytest discovery)
- AI tests: `Agile-LLM-main/test_scripts/test_api.py`
- load test: `test_scripts/load_test_p95.py`
- frontend tests: under `frontend/` (npm test)

## 4. Tooling

- `pytest` for Python services
- `React Testing Library` (via `npm test`) for frontend
- `Locust` for load testing
- OWASP ZAP quick scan for security sanity checks

## 5. Coverage Targets and Evidence

Reported quality baselines:

| Layer | Coverage | Tool |
|---|---|---|
| Backend | 85% | Pytest |
| Frontend | 75% | React Testing Library |
| AI service | 90% | Pytest |

## 6. Execution Guide

### 6.1 Backend tests

```bash
pip install -r requirements.txt
pytest
```

### 6.2 Frontend tests

```bash
cd frontend
npm install
npm test
```

### 6.3 AI service tests

```bash
cd Agile-LLM-main
pip install -r requirements.txt
pytest
```

### 6.4 Performance/load test

```bash
cd test_scripts
pip install locust
locust -f load_test_p95.py
```

Expected load profile outcomes:

| Concurrent users | Expected behavior | p95 latency |
|---|---|---|
| 10 | Stable | around 200 ms |
| 20 | Stable | around 350 ms |
| 25 | Stable with intentional login throttling | around 497 ms |

## 7. Security Verification

Verification points:

- invalid or missing token returns `401`
- unauthorized role access returns `403`
- rate-limit breach on auth path returns `429`

Sample scan command:

```bash
zap-cli quick-scan http://127.0.0.1:8000
```

## 8. Functional Regression Checklist

Before release, validate at least:

1. register/login/me flow
2. issue CRUD and status transitions
3. sprint CRUD and analytics views
4. profile create/update flow
5. AI progress and chat endpoints

## 9. Test Data and Demo Data

Use deterministic demo data for repeatable results:

- credentials: `demo/CREDENTIALS.txt`
- seed scripts: `demo/seed_v2.py` and related scripts

## 10. Exit Criteria

A build is release-ready when:

1. critical tests pass in all three services
2. no blocking security findings remain
3. load profile is within acceptable latency band
4. core user journeys complete without regression
