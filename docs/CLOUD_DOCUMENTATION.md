# IntelliTrack Cloud Implementation Documentation

This document explains how IntelliTrack is implemented on AWS in production, including the actual infrastructure components, deployment flow, service-to-service communication, reliability setup, and operational validation.

## 1. Cloud Implementation Summary

IntelliTrack runs as a cloud-native microservices platform on AWS with three runtime services:

- Frontend service (React plus Nginx)
- Backend API service (FastAPI)
- AI analysis service (FastAPI plus vector retrieval path)

Core implementation choices:

- Runtime compute: ECS Fargate
- Database: Amazon RDS for PostgreSQL (private, Multi-AZ)
- Networking entry point: Application Load Balancer
- Image registry: Amazon ECR
- Secret storage: AWS Secrets Manager
- Operational logs: Amazon CloudWatch Logs
- Infrastructure provisioning: Terraform
- Build and image publishing: AWS CodeBuild buildspecs

## 2. End-to-End Cloud Architecture

Traffic and service flow:

1. User requests reach the public Application Load Balancer.
2. ALB forwards API traffic to backend tasks running on ECS Fargate.
3. Backend accesses RDS PostgreSQL in private subnets.
4. Backend calls the AI microservice through internal service discovery.
5. AI service handles analysis and model integration workflows.
6. Logs from backend and AI tasks stream to CloudWatch log groups.
7. Container images are delivered from ECR, built through CI pipeline buildspecs.

## 3. Infrastructure Implemented with Terraform

The Terraform stack in terraform/main.tf provisions these components.

### 3.1 Network and Availability

- Dedicated VPC with CIDR 10.0.0.0/16
- 2 public subnets across 2 availability zones
- 2 private subnets across 2 availability zones
- Internet Gateway for public traffic
- 2 NAT Gateways (one per AZ) for private subnet outbound access
- Public and private route tables with explicit associations

### 3.2 Security Groups and Traffic Rules

- ALB security group:
   - Inbound 80 and 443 from 0.0.0.0/0
- ECS security group:
   - Inbound 8000-8004 only from ALB security group
   - Inbound 6333 from VPC CIDR for vector service access path
- RDS security group:
   - Inbound 5432 only from ECS security group

This design enforces least-exposure between internet, app runtime, and data layer.

### 3.3 Database Layer

- Engine: PostgreSQL 15.3
- DB name: intellitrack
- Storage: gp3, configurable size (default 20 GB)
- Availability: Multi-AZ enabled
- Public access: disabled
- Backup retention: 7 days
- CloudWatch PostgreSQL logs export enabled
- Final snapshot enabled on deletion

### 3.4 Secrets and Credentials

- Terraform creates a random database password.
- DATABASE_URL is stored in Secrets Manager under intellitrack/database-url.
- Runtime task definitions also consume secrets for:
   - database URL
   - JWT secret
   - OpenAI key
   - Qdrant URL and API key

### 3.5 Registry, Load Balancer, and Logs

- Three ECR repositories with image scan-on-push enabled:
   - intellitrack-backend
   - intellitrack-frontend
   - intellitrack-ai-service
- ALB plus backend target group:
   - Target type ip
   - Health check path /docs
- CloudWatch log groups:
   - /ecs/intellitrack-backend
   - /ecs/intellitrack-ai-service
   - 30-day log retention

## 4. ECS Runtime Configuration

### 4.1 Backend Task Definition

- Family: intellitrack-backend
- Fargate CPU and memory: 512 CPU, 1024 MB
- Port mapping: 8000
- Health check: /health endpoint every 30s
- Environment includes LLM model and internal AI service URL
- Uses Secrets Manager for sensitive values
- Logs to CloudWatch /ecs/intellitrack-backend

### 4.2 AI Service Task Definition

- Family: intellitrack-ai-service
- Fargate CPU and memory: 2048 CPU, 4096 MB
- Port mapping: 8004
- Health check: /health endpoint
- Secret injection for Qdrant API key
- Logs to CloudWatch /ecs/intellitrack-ai-service

### 4.3 Service Discovery and Internal Calls

Service Connect configuration is implemented for internal service name resolution under:

- Namespace: intellitrack.local
- AI service discovery name: intellitrack-ai-service
- Client alias DNS name: intellitrack-ai-service on port 8004

This supports resilient backend-to-AI internal communication without hardcoded IP dependencies.

## 5. CI and Deployment Implementation

### 5.1 Automated Build and Publish

The buildspec files implement per-service image workflows:

- buildspec/buildspec-backend.yml
- buildspec/buildspec-frontend.yml
- buildspec/buildspec-ai-service.yml

Pipeline behavior:

1. Login to ECR.
2. Build Docker image.
3. Tag latest and short commit hash.
4. Push both tags.
5. Emit imagedefinitions.json for deployment stages.

### 5.2 Deployment Script Flow

scripts/deploy.sh performs:

1. Prerequisite validation (AWS CLI, Docker, Terraform)
2. AWS credential validation
3. ECR repository creation if missing
4. Docker build and push for backend, frontend, AI service
5. Terraform init, plan, apply
6. Output capture (ALB DNS, RDS endpoint, IDs)
7. deployment-info.txt generation with next actions

## 6. Production Operations and Reliability

Implemented reliability controls:

- Multi-AZ database deployment
- Health checks at container and ALB layers
- Isolated microservices to limit blast radius
- CloudWatch log centralization for faster diagnosis
- Deployment output capture for deterministic post-deploy validation

Presentation-level reliability evidence captured in project artifacts:

- Stable behavior up to 25 concurrent users
- p95 latency around 497 ms under controlled login throttling
- Intentional rate limiting on auth path while core data endpoints stay responsive

## 7. Cloud Security Controls in Implementation

Cloud-layer security controls currently reflected in implementation and project security posture:

- Private database subnets with no public RDS exposure
- Security-group scoped east-west traffic
- Secret injection from Secrets Manager instead of static credentials
- Container image scanning on ECR push
- Health and log visibility for anomaly response
- HTTPS and WAF controls included in production architecture and security documentation

## 8. Deployment Validation Checklist

Run these checks after each deployment.

### 8.1 Infrastructure Validation

- Terraform apply completes with no drift errors
- ALB DNS output is available
- RDS endpoint output is available
- ECR repositories contain freshly pushed image tags

### 8.2 ECS Validation

- Backend and AI services are ACTIVE
- Desired count equals running count
- No repetitive restart loop in task events
- Task health checks pass

### 8.3 Functional Validation

- API documentation endpoint responds
- Health endpoint responds
- Backend can connect to RDS
- Backend to AI internal call path succeeds

### 8.4 Observability Validation

- Logs visible in both ECS log groups
- No startup secret resolution errors
- No sustained 5xx spikes in ALB target metrics

## 9. Gaps, Assumptions, and Next Hardening Steps

Items to keep improving based on current implementation state:

- Add explicit HTTPS listener and automatic HTTP to HTTPS redirect where not yet finalized
- Add autoscaling policies for ECS services in Terraform layer
- Add managed CloudWatch alarms and dashboards as code
- Add formal blue-green deployment controller configuration for ECS services
- Add Route 53 and ACM resources in Terraform for complete domain automation

## 10. Cloud Cost and Capacity Baseline

Current defaults in infrastructure variables show production-leaning but cost-aware sizing:

- Backend tasks: 512 CPU, 1024 MB, desired count 2
- AI service: 2048 CPU, 4096 MB, desired count 1
- RDS default class: db.t3.small

These values align with the observed workload profile and can be tuned through terraform/variables.tf based on traffic growth.