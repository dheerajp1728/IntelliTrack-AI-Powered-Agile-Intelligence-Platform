# IntelliTrack Code Documentation

This document explains the code structure, runtime architecture, and key API flows for IntelliTrack.

## 1. System Overview

IntelliTrack is split into three deployable services:

- Frontend: React + Vite SPA
- Backend API: FastAPI monolith for product features and auth
- AI Service: FastAPI microservice for repository indexing and AI analysis

High-level runtime flow:

1. User opens frontend and logs in.
2. Frontend calls backend endpoints with Bearer JWT.
3. Backend serves agile features (projects, sprints, issues, analytics, wiki).
4. AI requests go from backend to AI microservice (primary path).
5. Backend has a fallback path that can call OpenAI and Qdrant directly.

## 2. Repository Structure

### Root app project

- app/: backend Python application
- frontend/: React client application
- Agile-LLM-main/: AI analysis service
- buildspec/: CI buildspec files for CodeBuild
- docker/: Dockerfiles for backend, frontend, AI service
- ecs/: ECS service/task config files

### Backend package (app/)

- main.py: FastAPI app setup, middleware, routes, AI fallback logic
- auth.py: JWT creation/validation and password hashing
- database.py: SQLAlchemy engine/session setup
- models.py: SQLAlchemy ORM models and indexes
- schemas.py: Pydantic request/response models
- seed.py: seed data utilities

### Frontend package (frontend/src/)

- main.jsx: app bootstrap
- App.jsx: app-level route wiring and shell
- AuthContext.jsx: auth state, login/register/logout, token validation
- workspace/: main product UI pages and workspace features
- components/: shared UI components
- lib/: utility modules

### AI service package (Agile-LLM-main/)

- main.py: FastAPI endpoints (/health, /progress, /chat)
- code_indexer.py: repository fetch and embedding pipeline
- qdrant_indexer.py: Qdrant integration
- llm_analyzer.py: LLM task progress analysis
- repo_code_fetcher.py: GitHub repository fetch helpers
- test_scripts/test_api.py: API test script

## 3. Backend Architecture

### App bootstrap and middleware

The backend app is initialized in app/main.py with:

- CORS middleware using ALLOWED_ORIGINS
- Security headers middleware (HSTS, frame options, nosniff)
- IP-based rate limiting using slowapi
- Auto table creation via SQLAlchemy metadata
- Idempotent startup migrations for indexes and compatibility columns

### Data layer

- SQLAlchemy ORM models in app/models.py
- Session lifecycle in app/database.py
- Default local DB: SQLite file intellitrack.db
- Production DB: PostgreSQL via DATABASE_URL

Key modeled entities:

- User, DeveloperProfile
- Project, Sprint, Issue
- Comment, ActivityLog, Notification
- WikiPage, Label, Component, Release
- Legacy Task model for backward compatibility

### Authentication and authorization

- JWT with HS256 in app/auth.py
- Access token default expiry: 60 minutes
- Passwords hashed with PBKDF2-SHA256 + per-password salt
- Role-based checks for admin-only endpoints

## 4. API Surface (Backend)

The backend exposes a large REST API. Main route groups:

- Auth: /auth/register, /auth/login, /auth/me, /auth/change-password
- Users and profiles: /users, /users/{id}, /profiles, /profile/{user_id}
- Project and sprint management: /projects, /sprints, sprint start/complete
- Issue tracking: /issues, issue comments, activity, flagging
- Collaboration: /wiki, /notifications
- Planning metadata: /labels, /components, /releases
- Analytics: /analytics/sprint/{id}, /analytics/velocity, /analytics/workload, /analytics/cycle-time, /analytics/throughput
- Dashboard and search: /dashboard, /search
- Skill and workload endpoints: project members, user skills/history/workload, assignee recommendation
- AI gateway endpoints: /ai/health, /ai/analyze, /ai/chat

For complete schemas and live testing, use the backend OpenAPI docs at /docs.

## 5. AI Integration Design

### Primary path

When /ai/analyze or /ai/chat is called on the backend:

1. Backend tries the AI microservice first using LLM_SERVICE_URL.
2. AI microservice performs repository indexing/search and LLM analysis.
3. Backend returns the AI microservice result.

### Fallback path

If AI microservice is unavailable:

- Analyze fallback uses direct OpenAI prompt analysis.
- Chat fallback embeds the question, searches Qdrant, and asks OpenAI with retrieved code context.

This fallback prevents full feature outage during service discovery or DNS failures.

## 6. Frontend Architecture

Frontend is a Vite React app with API access through VITE_API_URL.

Auth flow implemented in frontend/src/AuthContext.jsx:

1. On startup, check token from localStorage.
2. Validate token with GET /auth/me.
3. Login/register stores access token in localStorage.
4. Subsequent requests send Authorization: Bearer <token>.
5. Logout clears local token and user state.

Main UI capabilities include:

- Dashboard views
- Agile board and sprint workflows
- Issue and backlog management
- Analytics/reporting pages
- Team and wiki modules

## 7. Environment Variables

### Backend required

- SECRET_KEY: required for JWT signing

### Backend optional/production

- DATABASE_URL: DB connection string (SQLite default if omitted)
- ALLOWED_ORIGINS: comma-separated CORS origins
- OPENAI_API_KEY: enables OpenAI-backed AI fallback
- LLM_SERVICE_URL: URL to AI microservice
- QDRANT_URL: used for AI chat fallback search
- QDRANT_API_KEY: optional Qdrant auth
- LLM_MODEL: optional model name override for AI calls

### Frontend

- VITE_API_URL: backend base URL

### AI service

- OPENAI_API_KEY and model/env settings used by AI modules
- Any GitHub token is passed per request to /progress when needed

## 8. Local Development

## 8.1 Backend

- Install Python dependencies from requirements.txt
- Set SECRET_KEY
- Run: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
- Swagger: http://127.0.0.1:8000/docs

## 8.2 Frontend

- Install node dependencies in frontend/
- Set VITE_API_URL (for example http://127.0.0.1:8000)
- Run: npm run dev

## 8.3 AI service

- Install dependencies in Agile-LLM-main/
- Ensure Qdrant is reachable
- Set OPENAI_API_KEY (or service-specific model settings)
- Run: uvicorn main:app --host 127.0.0.1 --port 8004

## 9. Build and Deployment Files

- Docker images:
  - docker/Dockerfile.backend
  - docker/Dockerfile.frontend
  - docker/Dockerfile.ai-service
- AWS task definitions and service config in ecs/
- CI buildspecs in buildspec/
- Infra as code in terraform/
- Helper scripts in scripts/

Related deployment docs:

- README_DEPLOYMENT.md
- AWS_DEPLOYMENT_BLUEPRINT.md
- QUICK_START.md
- TROUBLESHOOTING.md

## 10. Notes for Contributors

- Keep DB changes idempotent where possible (startup migration pattern is used).
- Preserve backward compatibility for legacy task endpoints when modifying issue workflows.
- When adding API routes, update both frontend integrations and this documentation.
- For AI features, validate both primary (LLM service) and fallback behavior.
