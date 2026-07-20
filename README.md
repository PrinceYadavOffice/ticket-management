# Support Ticket Management System

AI-assisted full-stack project for managing support tickets with comments, status workflows, and CSV export.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite, Vitest, React Testing Library |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | SQLite |
| Testing | Pytest (backend), Vitest + RTL (frontend) |

## Acting-User Context (Not Authentication)

This project uses a **seeded current-user selector** in the frontend. The selected user's ID is sent on every API request via the `X-User-Id` header. This establishes **acting-user context** for authorization and auditing—it is **not** authentication. See [api-contract.md](./api-contract.md) and [design-notes.md](./design-notes.md) for details.

## Repository Layout

```
├── README.md                    # This file
├── requirements-analysis.md     # Functional & non-functional requirements
├── acceptance-criteria.md     # Measurable acceptance criteria
├── implementation-plan.md       # Milestones, risks, Core vs Stretch
├── api-contract.md              # REST API specification
├── data-model.md                # Entity definitions
├── src/
│   ├── backend/                 # FastAPI application
│   └── frontend/                # React + Vite application
├── tests/                       # Backend & integration tests
├── database/
│   ├── migrations/              # Migration notes & references
│   └── seed-data/               # Seed scripts and fixtures
├── artifacts/                   # Generated artifacts & templates
└── ai-prompts/                  # AI session prompts by phase
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm or pnpm

## Quick Start

### Backend

```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example ../../.env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd src/frontend
npm install
npm run dev
```

### Run Tests

```bash
# Backend
cd src/backend && pytest ../../tests/backend ../../tests/integration -v

# Frontend
cd src/frontend && npm test
```

## Planning Artifacts

| Document | Purpose |
|----------|---------|
| [requirements-analysis.md](./requirements-analysis.md) | Requirements, assumptions, edge cases |
| [acceptance-criteria.md](./acceptance-criteria.md) | Testable acceptance criteria |
| [implementation-plan.md](./implementation-plan.md) | Phased delivery plan |
| [test-strategy.md](./test-strategy.md) | Testing approach |
| [api-contract.md](./api-contract.md) | API endpoints and contracts |

## Core vs Stretch

**Core** includes all mandatory entities, features, status state machine, validation, CSV export, and integration tests for status transitions.

**Stretch** (out of Core scope): real authentication, role-based UI, notifications, file attachments, pagination UI polish, deployment automation.

See [acceptance-criteria.md](./acceptance-criteria.md) for full boundaries.

## License

<!-- Add license if applicable -->
