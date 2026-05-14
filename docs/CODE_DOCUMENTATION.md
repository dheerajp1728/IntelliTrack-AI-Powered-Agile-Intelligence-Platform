# IntelliTrack Code Documentation

## 1. Purpose

This document explains how the IntelliTrack codebase is organized, how the main modules work, and where to extend functionality safely.

Intended audience:
- course evaluators
- maintainers and contributors
- new team members

## 2. System Architecture

IntelliTrack is a 3-service application:

1. Frontend: React + Vite (user interface)
2. Backend: FastAPI + SQLAlchemy (product/business API)
3. AI Service: FastAPI + Qdrant + OpenAI integration (analysis/chat)

High-level request flow:

1. User interacts with frontend.
2. Frontend sends API calls with `Authorization: Bearer <token>`.
3. Backend validates JWT and role permissions.
4. Backend reads/writes relational data through SQLAlchemy.
5. Backend calls AI service for AI-dependent endpoints.

## 3. Repository Structure

Core folders in this repository:

- `app/`: backend API source
- `frontend/`: frontend source
- `Agile-LLM-main/`: AI microservice source
- `docs/`: technical documentation
- `buildspec/`: AWS CodeBuild definitions
- `docker/`: Dockerfiles for all services
- `ecs/`: ECS Service Connect configuration
- `demo/`: demo credentials and data seed scripts
- `test_scripts/`: load and utility test scripts

## 4. Backend Implementation (`app/`)

### 4.1 Entry point: `app/main.py`

Main responsibilities:
- FastAPI app creation
- CORS configuration via `ALLOWED_ORIGINS`
- security headers middleware
- API route registration
- rate limiting using `slowapi`
- startup migrations (idempotent index/column setup)
- DB initialization (`Base.metadata.create_all`) and seed call

Security/operational middleware implemented:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Permissions-Policy`
- `Strict-Transport-Security`

Rate limiting examples:
- `/auth/register`: `5/minute`
- `/auth/login`: `10/minute`

### 4.2 Authentication: `app/auth.py`

Auth model:
- JWT (HS256) using `python-jose`
- token subject (`sub`) stores user email
- token TTL from `ACCESS_TOKEN_EXPIRE_MINUTES` (currently 60 minutes)

Password model:
- PBKDF2-HMAC-SHA256
- 100,000 iterations
- per-password random salt
- storage format: `salt$hash`

Key dependencies:
- `get_current_user_from_request()` validates bearer token on protected routes
- `check_user_role(required_roles)` for role-gated endpoints

### 4.3 Database: `app/database.py`

Storage strategy:
- local fallback: SQLite (`sqlite:///./intellitrack.db`)
- cloud: PostgreSQL via `DATABASE_URL`

Important behavior:
- auto-normalizes `postgres://` to `postgresql://`
- SQLAlchemy connection pooling enabled (`pool_pre_ping`, `pool_recycle`)

### 4.4 Data model: `app/models.py`

Primary entities:
- `User`
- `DeveloperProfile`
- `Project`
- `Sprint`
- `Issue`
- `Comment`
- `ActivityLog`
- `Notification`
- `WikiPage`
- `Component`
- `Label`
- `Release`

Compatibility note:
- `Task` model is retained for backward compatibility.
- Core workflow is issue-centric (`Issue` table and related endpoints).

Notable indexing:
- `ix_issues_project_id`
- `ix_issues_sprint_id`
- `ix_issues_assignee_id`
- `ix_issues_status`
- `ix_issues_project_sprint`

### 4.5 API contracts: `app/schemas.py`

Pydantic schemas define request/response boundaries for:
- auth (`UserLogin`, `UserRegister`, `Token`)
- profiles (`ProfileCreate`, `ProfileResponse`)
- project/sprint/issue CRUD
- analytics and dashboard payloads

## 5. Frontend Implementation (`frontend/`)

Key files:
- `frontend/src/main.jsx`: app bootstrap
- `frontend/src/App.jsx`: route/layout composition
- `frontend/src/AuthContext.jsx`: auth lifecycle and token persistence

Auth behavior in frontend:
- reads `VITE_API_URL`
- stores JWT in `localStorage`
- validates token on startup by calling `/auth/me`
- clears invalid token and user state automatically

Workspace UI modules (under `frontend/src/workspace/`) provide:
- board/backlog workflows
- sprint and issue interaction
- analytics/dashboard views

## 6. AI Service Implementation (`Agile-LLM-main/`)

Key files:
- `main.py`: AI API endpoints
- `llm_analyzer.py`: LLM analysis pipeline
- `qdrant_indexer.py`: vector database integration
- `code_indexer.py`: repository indexing/retrieval
- `repo_code_fetcher.py`: GitHub code fetch helpers
- `test_scripts/test_api.py`: service tests

Published AI endpoints:
- `GET /health`
- `POST /progress`
- `POST /chat`

Operational behavior in `POST /progress`:
- validates GitHub access
- indexes repository content into Qdrant
- retrieves relevant code chunks
- performs LLM task-progress analysis

## 7. Configuration and Environment Variables

### Backend (`app/`)

- `SECRET_KEY` (required)
- `DATABASE_URL`
- `ALLOWED_ORIGINS`
- `LLM_SERVICE_URL`
- `OPENAI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `LLM_MODEL`

### Frontend (`frontend/`)

- `VITE_API_URL`

### AI service (`Agile-LLM-main/`)

- `OPENAI_API_KEY`
- `LLM_MODEL`
- Qdrant connection/runtime variables

## 8. Build and Runtime Artifacts

Container definitions:
- `docker/Dockerfile.backend`
- `docker/Dockerfile.frontend`
- `docker/Dockerfile.ai-service`

Cloud build definitions:
- `buildspec/buildspec-backend.yml`
- `buildspec/buildspec-frontend.yml`
- `buildspec/buildspec-ai-service.yml`

Service connectivity configuration:
- `ecs/service-connect-backend.json`
- `ecs/service-connect-ai-service.json`

## 9. Engineering Conventions

Conventions followed:
- schema-validated API boundaries (Pydantic)
- separated auth/business/data concerns
- idempotent startup migrations and indexes
- explicit role checks for sensitive operations
- reproducible container builds per service

## 10. Extension Guide

When adding a new backend feature:

1. add/adjust ORM fields in `app/models.py`
2. add Pydantic contracts in `app/schemas.py`
3. add endpoints in `app/main.py`
4. secure endpoint with auth/role dependency
5. add/update tests
6. update relevant docs in `docs/`

When adding a new AI capability:

1. add endpoint in `Agile-LLM-main/main.py`
2. implement retrieval/analyzer logic in AI modules
3. wire backend gateway call if needed
4. add API tests in `Agile-LLM-main/test_scripts/`
