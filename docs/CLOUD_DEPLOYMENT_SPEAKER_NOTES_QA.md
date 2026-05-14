# IntelliTrack Cloud Deployment, Speaker Notes, and Viva Q&A

This document is designed for software engineering course presentation use. It combines:
- Full deployment implementation details
- A brief speaker script you can present confidently
- High-probability professor questions with strong answers

## 1. What We Actually Implemented on AWS

### 1.1 Runtime Architecture

IntelliTrack is deployed as a microservices system:
- Frontend service: React + Nginx container
- Backend API service: FastAPI container
- AI service: FastAPI-based AI microservice container
- Data layer: Amazon RDS PostgreSQL

### 1.2 Core AWS Services Used

Used in implementation:
- ECS Fargate: container runtime for backend and AI services
- ECR: Docker image registry
- RDS (PostgreSQL): managed relational database
- ALB: public traffic entry and routing to backend
- VPC, subnets, route tables, NAT, security groups: networking foundation
- Secrets Manager: runtime secrets and credentials
- CloudWatch Logs: centralized logs
- IAM: service roles and least-privilege role separation
- Cloud Map / Service Discovery (Service Connect namespace intellitrack.local): internal DNS/service resolution
- CodeBuild: cloud build system for image build and push
- S3 (in cloud build workflow): source packaging for CodeBuild

Not implemented as primary deployment engine:
- CodePipeline: not found in IaC/scripts as active orchestrator
- Aurora: not used (RDS PostgreSQL is used)
- EC2 instances: not used for app compute (Fargate is used). EC2 APIs are used indirectly for networking resources.

### 1.3 CodeBuild vs Terraform Clarification

Both are used, but for different responsibilities:
- CodeBuild handles build stage: builds Docker images and pushes them to ECR.
- Terraform handles infrastructure stage: creates networking, database, load balancer, repositories, and logging resources.
- ECS CLI/service creation steps then register task definitions and create services.

So deployment is a combined flow, not CodeBuild-only and not Terraform-only.

## 2. End-to-End Deployment Flow We Followed

This is the practical sequence from our deployment scripts and configuration.

### Step 0: Input and secret preparation
- Collected runtime secrets (JWT, OpenAI key, Qdrant settings where applicable).
- Stored/updated secrets in AWS Secrets Manager.

### Step 1: Build system bootstrap
- Created or updated CodeBuild IAM role.
- Attached ECR and logging permissions.
- Uploaded zipped source bundle to S3 for CodeBuild projects.

### Step 2: Cloud build stage
- Created/updated 3 CodeBuild projects:
  - backend buildspec
  - frontend buildspec
  - ai-service buildspec
- Triggered builds and monitored status.
- Pushed latest and commit-based tags to ECR.

### Step 3: Infrastructure provisioning stage (Terraform)
- Initialized Terraform state.
- Applied infrastructure plan to create AWS resources:
  - VPC with public and private subnets in 2 AZs
  - Internet gateway, NAT gateways, route tables
  - ALB and backend target group
  - RDS PostgreSQL (Multi-AZ, private)
  - Security groups for ALB, ECS, and RDS
  - ECR repositories
  - CloudWatch log groups
  - Secrets Manager entry for generated DB URL

### Step 4: ECS runtime deployment stage
- Created ECS cluster.
- Created ECS task IAM roles.
- Registered backend and AI task definitions.
- Created ECS services with private subnet networking.
- Connected backend to AI endpoint through internal service discovery.

### Step 5: Post-deployment validation
- Verified service/task status (ACTIVE and running counts).
- Verified health checks and target group health.
- Verified API availability via ALB URL.
- Verified backend and AI logs in CloudWatch.
- Seeded database/demo data for application validation.

## 3. Networking and Security Implementation Details

### 3.1 Network design
- Public ALB receives external traffic.
- ECS services run in private subnets.
- RDS is private only, no public exposure.
- NAT provides controlled outbound internet for private workloads.

### 3.2 Security boundaries
- ALB SG allows inbound 80 and 443 from internet.
- ECS SG accepts app ports only from ALB SG.
- RDS SG accepts 5432 only from ECS SG.
- Secrets are pulled at runtime from Secrets Manager.

### 3.3 Operational security controls
- Image scan on push in ECR repositories.
- Health checks at container and ALB layers.
- CloudWatch logs for audit and failure triage.
- IAM role separation for CodeBuild and ECS tasks.

## 4. Reliability and Performance Evidence for Presentation

Key outcomes you can claim:
- 3 production microservices deployed.
- Stable behavior up to 25 concurrent users.
- Average latency around 232 ms and p95 near 497 ms under tested load profile.
- Rate limiting intentionally throttles heavy login bursts while business endpoints remain responsive.
- AI service fallback path reduced impact from service discovery or DNS instability events.

## 5. 2-Minute Speaker Notes (Brief Delivery)

Use this if your professor asks for a short deployment explanation.

"Our deployment is cloud-native and service-oriented. We split the system into backend, frontend, and AI microservices. For CI, we use CodeBuild to build Docker images and push them to ECR. For infrastructure, we use Terraform to provision VPC networking, ALB, RDS, security groups, and logging.

After infrastructure comes up, we register ECS task definitions and create Fargate services for backend and AI. The backend talks to the AI service using internal service discovery under intellitrack.local. Secrets like DB URL and JWT key are not hardcoded; they are injected from Secrets Manager.

For reliability, we run health checks at both container and ALB level, use Multi-AZ RDS, and monitor logs in CloudWatch. In performance tests, the app stayed stable up to 25 concurrent users, with login throttling intentionally enforced for security."

## 6. 5-Minute Speaker Notes (Rubric-Friendly)

Use this when you need an outcome -> decision -> evidence structure.

### 6.1 Outcome
"Our goal was to deploy a production-style agile platform, not just run a local demo."

### 6.2 Key decisions
- "We used microservices to isolate failures and scale independently."
- "We chose ECS Fargate to avoid EC2 server management overhead."
- "We separated build and infra responsibilities: CodeBuild for image build, Terraform for infrastructure provisioning."
- "We used Secrets Manager and strict security groups to reduce credential and network exposure risk."

### 6.3 Evidence
- "Three services are deployed in AWS and integrated through ALB and service discovery."
- "RDS runs in private subnets with controlled SG access."
- "CloudWatch logs and health checks support operational debugging."
- "Load tests show stable operation up to 25 concurrent users with acceptable p95 latency."

### 6.4 Engineering lesson
"The biggest challenge was deployment reliability and networking, not writing endpoints. Service discovery and health checks were critical to make the architecture production-ready."

## 7. High-Probability Professor Questions and Strong Answers

### Q1. Did you use CodeBuild or Terraform for deployment?
A: "Both. CodeBuild handles build/push of container images to ECR. Terraform provisions cloud infrastructure. ECS service creation and task registration complete runtime deployment."

### Q2. Why ECS Fargate and not EC2 or Kubernetes?
A: "Fargate reduced operational overhead and matched our course timeline. We avoided cluster/node management and focused on service reliability and delivery quality."

### Q3. Did you use CodePipeline?
A: "In our implementation, CodeBuild and deployment scripts are active. CodePipeline is not the active orchestrator in the current repository-based deployment flow."

### Q4. Are you using Aurora?
A: "No. We use Amazon RDS PostgreSQL through aws_db_instance configuration, not Aurora cluster resources."

### Q5. How is internal backend to AI communication handled?
A: "Through internal service discovery using Cloud Map/Service Connect namespace and service aliasing, so calls do not depend on static IPs."

### Q6. How are secrets handled securely?
A: "Secrets are stored in AWS Secrets Manager and injected into ECS task runtime. We avoid committing secret values in source code or task definition plaintext when possible."

### Q7. What security controls are in the cloud layer?
A: "Private subnets for compute and DB, SG-restricted traffic, Secrets Manager, image scan-on-push, and runtime health/log monitoring."

### Q8. What was the hardest deployment issue?
A: "Service discovery and health check alignment. Incorrect DNS discovery or endpoint checks caused startup instability. We fixed this with explicit namespace/service config and stronger validation checks."

### Q9. How did you validate deployment success?
A: "We validated Terraform outputs, ECS service/task state, ALB target health, API endpoint availability, database connectivity, and CloudWatch logs."

### Q10. What would you improve next?
A: "Formal blue-green rollout as code, autoscaling policies in Terraform, Route53/ACM automation, and dashboards/alarms as code."

### Q11. Why microservices for a student project?
A: "Because our goal included realistic cloud deployment and reliability engineering practice. Splitting AI and backend gave us clearer fault isolation and independent deployment paths."

### Q12. What software engineering concepts does this demonstrate?
A: "Separation of concerns, infrastructure-as-code, CI-driven containerization, secure secret management, operational observability, and reliability-focused iterative refinement."

## 8. Short Closing Statement for Viva

"IntelliTrack demonstrates full software engineering lifecycle maturity: from architecture design to cloud deployment, observability, security hardening, and performance validation. Our strongest learning was that production reliability depends more on infrastructure correctness and deployment discipline than on feature code alone."

## 9. One-Page Rapid Revision (Pre-Presentation)

Memorize these points:
- Build stage: CodeBuild -> ECR
- Infra stage: Terraform
- Runtime stage: ECS Fargate services
- Data: RDS PostgreSQL private + Multi-AZ
- Secrets: Secrets Manager
- Internal service communication: Cloud Map/Service Connect
- Security: SG boundaries + secret injection + image scanning
- Reliability evidence: health checks + CloudWatch + load test results
- Main lesson: deployment and operations complexity drove architecture decisions
