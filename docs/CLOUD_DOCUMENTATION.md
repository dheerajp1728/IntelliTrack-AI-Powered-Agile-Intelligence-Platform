# IntelliTrack Cloud Documentation

## 1. Purpose

This document describes the AWS deployment model used by IntelliTrack, including build, release, runtime connectivity, and operations checks.

## 2. Runtime Architecture (AWS)

Primary runtime services:

- frontend container (Nginx + built Vite app)
- backend container (FastAPI)
- AI service container (FastAPI)

Primary AWS services:

- Amazon ECS Fargate (service runtime)
- Amazon ECR (container registry)
- AWS CodeBuild (build and deploy trigger)
- Application Load Balancer (public entry)
- Amazon RDS PostgreSQL (persistent relational data)
- AWS Secrets Manager (runtime secrets)
- Amazon CloudWatch Logs (service logs)
- Service Connect / Cloud Map namespace: `intellitrack.local`

## 3. Build and Deploy Pipeline

Repository buildspec files:

- `buildspec/buildspec-backend.yml`
- `buildspec/buildspec-frontend.yml`
- `buildspec/buildspec-ai-service.yml`

Pipeline pattern per service:

1. login to ECR
2. build Docker image using service Dockerfile
3. push `latest` and short-commit-tag image
4. force new ECS deployment
5. wait for service stability

CodeBuild project definitions are tracked in:

- `update-backend.json`
- `update-frontend.json`
- `update-ai-service.json`

## 4. Containerization

Container definitions:

- `docker/Dockerfile.backend`
- `docker/Dockerfile.frontend`
- `docker/Dockerfile.ai-service`

Notable hardening choices:

- non-root users in backend and AI images
- explicit health checks in all three Dockerfiles
- minimal base images (`python:3.11-slim`, `node:20-alpine`, `nginx:alpine`)

## 5. Service Connectivity

Service Connect settings:

- `ecs/service-connect-backend.json`
- `ecs/service-connect-ai-service.json`

Namespace:

- `intellitrack.local`

Purpose:

- stable internal service discovery
- reduced dependency on hardcoded private IP routing

## 6. Operational Verification Checklist

After deployment, verify:

1. ECS service `desired == running` for all services
2. ECS deployment status is stable
3. ALB targets are healthy
4. backend API responds (`/` and auth endpoints)
5. AI service health endpoint responds (`/health`)
6. CloudWatch logs have no startup/secret failures

## 7. Performance Baseline

Observed project baseline:

- stable behavior under 25 concurrent users
- p95 latency in tested scenario around 497 ms
- login route throttling is intentional for abuse protection

Load test script:

- `test_scripts/load_test_p95.py`

## 8. Environment and Secrets

Runtime variables are injected through environment configuration and AWS secret management.

Critical variables include:

- `SECRET_KEY`
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `LLM_MODEL`

## 9. Known Repository Boundary

This repository contains deployment/build/runtime configuration for ECS and CodeBuild.

If full Terraform IaC is maintained externally or in a different folder/repository, keep this document synchronized with the actual source of truth used for production changes.

## 10. Recommended Improvements

1. codify autoscaling policies per ECS service
2. codify CloudWatch alarms and dashboards
3. enforce image vulnerability gates in CI
4. add structured deployment rollback runbook
