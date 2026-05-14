# Demo Folder

This folder contains demo credentials, seed scripts, and demo-related files for IntelliTrack.

## Files

- **CREDENTIALS.txt** — Demo user credentials and login information for the IntelliTrack application
- **seed_demo.py** — Demo seed script for Render deployment (creates users, projects, sprints, and issues)
- **seed_fix.py** — Quick fix seed script for demo data
- **seed_v2.py** — AWS ECS deployment demo seed script (creates realistic demo data for 7 sprints)

## Usage

### Running seed_v2.py (AWS ECS Deployment)

This is the recommended seed script for the live AWS deployment:

```bash
python seed_v2.py
```

This script will:
1. Register/login team members
2. Create developer profiles
3. Create the main IntelliTrack project
4. Seed labels and components
5. Create 7 sprints (S1–S6 completed, S7 active)
6. Create 50+ realistic issues across all sprints
7. Add realistic comments from team members

### Running seed_demo.py (Render Deployment)

For legacy Render deployment:

```bash
python seed_demo.py
```

### Demo Credentials

All demo users have password: `Track2026!`

| Role | Name | Email |
|---|---|---|
| Admin | Raunak | raunak@intellitrack.dev |
| Scrum Master | Vignesh | vignesh@intellitrack.dev |
| Backend Dev | Dheeraj | dheeraj@intellitrack.dev |
| Frontend Dev | Hemanesh | hemanesh@intellitrack.dev |
| Full Stack / AI | Upasana | upasana@intellitrack.dev |

## Demo Flow

1. Use the credentials to log in to http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com
2. Explore the dashboard, board, backlog, and analytics
3. Try drag-and-drop on the Kanban board
4. Create new issues or sprints
5. Use the AI analysis features (if AI service is available)

## Notes

- Each seed script is idempotent — running it twice will use existing data
- The scripts use environment variable `BASE` to target different deployments
- Ensure the backend API is running before executing seed scripts
