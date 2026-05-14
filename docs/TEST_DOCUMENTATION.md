# IntelliTrack Test Documentation

This document outlines the testing strategy, test coverage, comparative analysis, and instructions for running IntelliTrack tests. All testing follows the methodology and metrics defined in the **Final Project Report (May 2026)**.

**Test Scripts Location:** All load and performance tests are located in the [test_scripts/](../test_scripts/) folder at the repository root.

## 1. Testing Strategy (As Per Final Report Section 8)

### Types of Tests

1. **Unit Tests**: Validate individual functions and methods.
2. **Integration Tests**: Test interactions between backend, database, and AI service.
3. **End-to-End Tests**: Simulate user workflows across frontend and backend.
4. **Performance Tests**: Measure API latency and concurrency limits.
5. **Security Tests**: Verify authentication, rate limiting, and OWASP compliance.

### Tools Used

- **Pytest**: For backend unit and integration tests.
- **React Testing Library**: For frontend component tests.
- **Locust**: For load testing.
- **OWASP ZAP**: For security testing.

## 2. Comparative Test Analysis

### Performance Testing Results

| Concurrent Users | Result | p95 Latency |
|---|---|---|
| 10 users | Stable | ~200 ms |
| 20 users | Stable | ~350 ms |
| 25 users | Stable with intentional rate limiting | 497 ms (login throttled) |

### Security Testing Results

- **JWT Authentication**: Enforced on all protected endpoints.
- **Rate Limiting**: 10 requests/minute on login endpoint.
- **SQL Injection**: Prevented via parameterized queries.
- **XSS Protection**: Enabled via AWS WAF.

## 3. Testing Instructions

### Backend Tests

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

### Frontend Tests

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run tests:
   ```bash
   npm test
   ```

### Load Testing

**Location:** [test_scripts/load_test_p95.py](../test_scripts/load_test_p95.py)

1. Install Locust:
   ```bash
   pip install locust
   ```

2. Run load tests against the live deployment:
   ```bash
   cd test_scripts
   locust -f load_test_p95.py
   ```

3. Configure concurrency levels (default: 25 concurrent users):
   - Opens browser to http://localhost:8089
   - Adjust spawn rate and target concurrency
   - Runs against: http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com

**Report Results:** Tests measure p95 latency under 10, 20, and 25 concurrent users. Expected results from Final Report:
- 10 users: ~200ms p95 latency
- 20 users: ~350ms p95 latency  
- 25 users: ~497ms p95 latency (login endpoint rate-limited intentionally; data endpoints remain <200ms)

### Security Testing

1. Run OWASP ZAP:
   ```bash
   zap-cli quick-scan http://127.0.0.1:8000
   ```

2. Analyze the report for vulnerabilities.

## 4. Test Coverage

As reported in **Final Project Report Section 8.3**:

| Layer | Coverage | Tool | Status |
|---|---|---|---|
| **Backend (API + logic)** | 85% code coverage | Pytest + SQLAlchemy fixtures | ✅ Sprint 7 |
| **AI Service endpoints** | 90% endpoint coverage | Pytest unit tests per component | ✅ Sprint 7 |
| **Frontend components** | 75% component coverage | React Testing Library | ✅ Sprint 7 |
| **Load testing** | 25 concurrent users | Locust (test_scripts/) | ✅ Verified |
| **Security scanning** | OWASP Top 10 | OWASP ZAP + manual testing | ✅ Sprint 7 |

## 5. Testing Strategy by Type (Final Report Section 8.4)

### Unit Tests — Per Component
- **Backend**: JWT creation, PBKDF2 verification, role checks tested independently
- **AI**: Each scoring component (skill match, workload, experience, availability) has dedicated unit tests
- **Frontend**: Form validation, role-scoped views, Kanban interactions tested with React Testing Library

### Integration Tests — Service Boundaries
- **Framework**: Pytest with SQLAlchemy test fixtures
- **Scope**: Authentication endpoints, profile CRUD, task assignment logic, AI scoring pipeline end-to-end
- **Enforcement**: GitHub Actions CI blocks merge if test fails (Sprint 7 rule)

### Performance Tests — Load and Latency
- **Tool**: Locust (test_scripts/load_test_p95.py)
- **Environment**: Against deployed AWS ECS Fargate environment
- **Metrics**: p95 latency under 10, 20, 25 concurrent users

### Security Tests — OWASP and Auth
- **OWASP ZAP**: Quick-scan before each sprint to detect injection, auth, and exposure vulnerabilities
- **JWT**: Enforced on all protected endpoints; unauthenticated requests confirmed return 401
- **Rate Limiting**: 10 requests/minute on login; confirmed returns 429 at threshold

### Manual Testing — Demo Readiness
- All sprint demos conducted on **live PostgreSQL data** (no mocks) from Sprint 5 onward
- Role-based views manually verified for all 3 roles before each demo
- 10-step pre-demo checklist: login, task creation, AI assignment, chat, Kanban, dashboard, risk badges

## 6. Deployment and Test Verification

**Live Deployment:** http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com

**Test Data:** Use demo credentials from [demo/CREDENTIALS.txt](../demo/CREDENTIALS.txt):
```
All passwords: Track2026!
- Raunak (Admin)
- Vignesh (Scrum Master)
- Dheeraj (Backend Developer)
- Hemanesh (Frontend Developer)
- Upasana (Full Stack / AI)
```

Or run seed scripts from [demo/](../demo/):
```bash
python demo/seed_v2.py  # AWS ECS deployment (recommended)
python demo/seed_demo.py  # Render deployment (legacy)
```

## 7. Notes for Testers

- **Backend Setup**: Ensure backend is running before frontend tests
- **Test Data**: Use consistent seed data from demo/ folder for reproducibility
- **Load Testing**: Run from test_scripts/ directory to ensure proper path resolution
- **Report Issues**: File issues with test results and environment details in GitHub
- **CI/CD**: All tests enforced in GitHub Actions pipeline before merge to main