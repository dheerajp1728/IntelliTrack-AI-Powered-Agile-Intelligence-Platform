# IntelliTrack — AI-Assisted Agile Project Tracking Platform

> Production-grade sprint management with intelligent task assignment and GitHub integration.

**IntelliTrack** is a full-stack Agile project management platform designed for software development teams of 2–10 developers. Built over 7 two-week sprints, the system delivers:
- **Sprint Planning & Kanban Board** with drag-and-drop task management
- **AI Task Assignment** using a 105-point scoring engine (skill, workload, experience, availability)
- **Natural Language AI Chat** for sprint Q&A and analysis
- **Production AWS Deployment** on ECS Fargate with sub-130ms p95 latency
- **83.3% average sprint velocity** across 7 sprints (305 of 366 story points delivered)

**Live Deployment:** http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com/  
**GitHub Repository:** https://github.com/dheerajp1728/IntelliTrack-AI-Powered-Agile-Intelligence-Platform

---

## 📋 Documentation

All comprehensive documentation is organized in the [docs/](docs/) folder:

- **[docs/CODE_DOCUMENTATION.md](docs/CODE_DOCUMENTATION.md)** — Full codebase architecture, API reference, models, and backend/frontend structure
- **[docs/TEST_DOCUMENTATION.md](docs/TEST_DOCUMENTATION.md)** — Testing strategy, test coverage (85% backend, 75% frontend), load testing results, and security verification
- **[docs/SECURITY_DOCUMENTATION.md](docs/SECURITY_DOCUMENTATION.md)** — Security hardening, OWASP compliance, and vulnerability mitigations
- **[docs/CLOUD_DOCUMENTATION.md](docs/CLOUD_DOCUMENTATION.md)** — CloudWatch metrics, monitoring, and production operations
- **[docs/README.md](docs/README.md)** — Documentation index and maintenance standards

### Demo & Testing

- **[demo/](demo/)** — Demo credentials, seed scripts, and demo data
- **[test_scripts/](test_scripts/)** — Load testing with Locust (25 concurrent users, p95 latency measurement)

---

## Repository Structure

```
IntelliTrack-AI-Powered-Agile-Intelligence-Platform/
├── app/                           # FastAPI backend
│   ├── main.py                   # API routes, middleware, startup
│   ├── models.py                 # SQLAlchemy ORM (User, Sprint, Task, etc.)
│   ├── schemas.py                # Pydantic request/response models
│   ├── auth.py                   # JWT, PBKDF2, authentication
│   ├── database.py               # SQLAlchemy session and engine
│   └── seed.py                   # Demo data seeder
├── frontend/                      # React + Vite frontend
│   ├── src/
│   │   ├── AuthContext.jsx       # JWT auth state
│   │   ├── App.jsx               # Main router
│   │   ├── workspace/            # Dashboard, board, backlog, analytics
│   │   └── components/           # Shared UI components
│   ├── package.json
│   └── vite.config.js
├── Agile-LLM-main/               # AI microservice (separate project)
│   ├── main.py                   # FastAPI AI endpoints
│   ├── code_indexer.py           # GitHub repo indexing
│   ├── qdrant_indexer.py         # Vector database client
│   ├── llm_analyzer.py           # LLM analysis logic
│   └── test_scripts/             # AI service tests
├── buildspec/                     # AWS CodeBuild configs
│   ├── buildspec-backend.yml
│   ├── buildspec-frontend.yml
│   └── buildspec-ai-service.yml
├── docker/                        # Dockerfiles
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.ai-service
├── ecs/                           # AWS ECS task definitions
│   ├── backend-task-definition.json
│   ├── frontend-task-definition.json
│   └── ai-service-task-definition.json
├── docs/                          # ✨ Documentation (NEW)
│   ├── CODE_DOCUMENTATION.md
│   ├── TEST_DOCUMENTATION.md
│   ├── SECURITY_DOCUMENTATION.md
│   ├── CLOUD_DOCUMENTATION.md
│   └── README.md
├── demo/                          # ✨ Demo & Seed Scripts (NEW)
│   ├── CREDENTIALS.txt            # Demo user credentials
│   ├── seed_v2.py                # AWS ECS seed script
│   ├── seed_demo.py              # Render deployment seed
│   └── README.md                 # Demo folder guide
├── test_scripts/                  # ✨ Load Testing (NEW)
│   ├── load_test_p95.py          # Locust load test
│   └── test_chat.py
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── render.yaml                    # Optional Render deployment config
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- AWS Account (for deployment; optional for local dev)

### Local Development (Under 10 minutes)

1. **Clone and Setup Backend**
   ```bash
   git clone https://github.com/dheerajp1728/IntelliTrack-AI-Powered-Agile-Intelligence-Platform
   cd IntelliTrack-AI-Powered-Agile-Intelligence-Platform
   pip install -r requirements.txt
   export SECRET_KEY="your-secret-key-here"
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   # Opens http://localhost:5173
   ```

3. **Seed Demo Data (Optional)**
   ```bash
   python demo/seed_v2.py
   ```

4. **Login**
   - Use credentials from [demo/CREDENTIALS.txt](demo/CREDENTIALS.txt)
   - All demo passwords: `Track2026!`

---

## 🧪 Testing

All tests follow the methodology in **[docs/TEST_DOCUMENTATION.md](docs/TEST_DOCUMENTATION.md)**:

### Run Backend Tests
```bash
pytest  # 85% code coverage, all integration tests
```

### Run Frontend Tests
```bash
cd frontend
npm test  # 75% component coverage
```

### Load Testing (25 Concurrent Users)
```bash
cd test_scripts
pip install locust
locust -f load_test_p95.py
# Opens http://localhost:8089
```

**Expected Results** (from Final Report Section 8):
- 10 users: ~200ms p95 latency ✅
- 20 users: ~350ms p95 latency ✅
- 25 users: ~497ms p95 latency (login rate-limited; data endpoints <200ms) ✅

---

## 🏗️ Architecture

### Three-Service Deployment (AWS ECS Fargate)

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19 + Vite | SPA with drag-and-drop board, real-time updates |
| **Backend** | FastAPI + SQLAlchemy | REST API, role-based auth, 60+ endpoints |
| **Database** | PostgreSQL 15 (RDS) | Relational data: users, sprints, tasks, profiles |
| **AI Service** | FastAPI microservice | Qdrant vector search + OpenAI GPT-4o-mini |
| **Vector DB** | Qdrant Cloud | Semantic similarity for task assignment |
| **AI LLM** | OpenAI GPT-4o-mini | Chat completions, embeddings, analysis |
| **Auth** | JWT + PBKDF2-SHA256 | Stateless auth, role-based access (Admin, Scrum Master, Developer) |
| **Load Balancing** | AWS ALB | Path routing, blue/green deployments |
| **WAF** | AWS WAF | SQL injection, XSS, DDoS protection |
| **Monitoring** | CloudWatch | CPU, memory, latency, custom metrics |
| **CI/CD** | GitHub Actions + CodeBuild | Automated test, build, push, deploy (6 min end-to-end) |

---

## 🎯 Key Features

### 1. Sprint Management
- ✅ Sprint creation with capacity tracking and goals
- ✅ Sprint lifecycle: Planning → Active → Completed
- ✅ Velocity tracking and burn-down charts (D3.js)

### 2. Task & Backlog Management
- ✅ Full CRUD for Stories, Bugs, Tasks, Epics, Sub-tasks
- ✅ Story point estimation and priority levels
- ✅ Required skills tagging for AI matching
- ✅ Risk detection badges (Stale, At-Risk, Failing CI, Large Diff)

### 3. AI Task Assignment (105-Point Scoring)
- ✅ Skill match (30 pts) — fuzzy keyword matching
- ✅ Workload balance (40 pts) — (1 - active_points/capacity) formula
- ✅ Experience (15 pts) — count of completed tasks
- ✅ Availability (10 pts) — Available/Partial/On-Leave status
- ✅ Keyword bonus (10 pts) — tech terms from task title/description

**Result:** Returns top 3 ranked candidates with plain-language reasoning strings.

### 4. AI Chat Assistant
- ✅ Under 1.5s response time (after context compression)
- ✅ Sprint status queries
- ✅ At-risk task detection
- ✅ Team workload analysis
- ✅ PR review prioritization

### 5. Kanban Board
- ✅ Drag-and-drop with @dnd-kit
- ✅ Columns: To Do, In Progress, In Review, Done
- ✅ Real-time status updates
- ✅ Risk badges on cards
- ✅ Optimistic UI with rollback on error

### 6. Developer Profiles
- ✅ Skills, experience level, capacity, availability
- ✅ Auto-suggested skills from Git history
- ✅ Workload calculator
- ✅ Task history and completed count

### 7. Analytics & Reporting
- ✅ Velocity chart (committed vs completed points per sprint)
- ✅ Burn-down graph (ideal vs actual remaining points)
- ✅ Team workload heatmap
- ✅ Sprint completion ring
- ✅ Recent activity feed

---

## 📊 Performance & Metrics

**From Final Report (Section 8):**

| Metric | Target | Achieved | Source |
|---|---|---|---|
| API p95 latency | <200ms | 130ms max | CloudWatch under 25 users |
| AI assignment | <10s | 8s avg | 3 ranked candidates |
| AI chat response | <3s | <1.5s | GPT-4o-mini with compression |
| Sprint velocity | ≥80% | 83.3% | 305/366 story points |
| Load capacity | 25 users | 25 users ✅ | Locust load test |
| Test coverage (backend) | — | 85% | Pytest |
| Test coverage (frontend) | — | 75% | React Testing Library |

---

## 🚀 Deployment

### Live Production (AWS ECS Fargate)
- **URL:** http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com
- **Region:** us-east-1
- **Services:** 3 microservices (frontend, backend, AI) on ECS Fargate
- **Database:** RDS PostgreSQL 15 with automated daily backups
- **Security:** AWS WAF + CloudTrail + Secrets Manager
- **CI/CD:** GitHub Actions → CodeBuild → ECR → ECS (6 min deploy)
- **Monitoring:** CloudWatch metrics and alarms

### Deploy Locally with Docker Compose
```bash
# (Optional) For local multi-service testing
docker-compose up -d
```

See **[docs/CLOUD_DOCUMENTATION.md](docs/CLOUD_DOCUMENTATION.md)** for deployment details.

---

## 🎮 Try the Live Demo

**URL:** http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com

**Demo Credentials** (see [demo/CREDENTIALS.txt](demo/CREDENTIALS.txt)):
```
Admin:           Raunak          | raunak@intellitrack.dev
Scrum Master:    Vignesh         | vignesh@intellitrack.dev
Backend Dev:     Dheeraj         | dheeraj@intellitrack.dev
Frontend Dev:    Hemanesh        | hemanesh@intellitrack.dev
Full Stack / AI: Upasana         | upasana@intellitrack.dev

All passwords: Track2026!
```

Or seed fresh demo data:
```bash
python demo/seed_v2.py  # AWS ECS deployment
```

---

## 👥 Team

Built by 5 developers over 7 two-week sprints:

| Name | Role | Key Contributions |
|---|---|---|
| Raunak Ahmed | Engineering Lead | System architecture, FastAPI backend, AWS ECS |
| Vignesh Shanmugasundaram | Full Stack / Scrum Master | Sprint management, Kanban UI, task CRUD |
| Dheeraj Pakala | Backend / Product Owner | REST API design, database models, deployment |
| Hemanesh Kamireddy | Frontend / DevOps | React UI, dashboards, infrastructure |
| Upasana Chakraborty | AI / Full Stack | OpenAI integration, Qdrant indexing, embeddings |

---

## 📈 Project Metrics

- **Duration:** 7 two-week sprints (14 weeks)
- **Story Points:** 305 of 366 delivered (83.3% velocity)
- **Sprint Performance:** 93%, 92%, 92%, 70%, 81%, 85%, 79%
- **Code Coverage:** Backend 85%, Frontend 75%, AI Service 90%
- **Load Tested:** 25 concurrent users, p95 latency <500ms
- **Deployment Time:** ~6 minutes (GitHub push to ECS stable)
- **Uptime:** 99.9% on AWS ECS Fargate

---

## 📝 License

[Add your license here if applicable]

---

## 🔗 Links

- **Repository:** https://github.com/dheerajp1728/IntelliTrack-AI-Powered-Agile-Intelligence-Platform
- **Live Deployment:** http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com
- **Final Report:** See [docs/](docs/) folder
- **Demo Credentials:** [demo/CREDENTIALS.txt](demo/CREDENTIALS.txt)

---

**IntelliTrack** — Making sprint management smarter with AI. 🚀
