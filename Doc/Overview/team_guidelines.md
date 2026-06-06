# Team Guidelines
**AC Supply Chain AI · American Computers Albania**
**Faculty of Information Technology**

---

## Project

We are building an AI-powered supply chain management system for American Computers Albania, an electronics retailer in Tirana. The system gives retail managers a live inventory dashboard, per-category demand forecasts using ARIMA, and automated anomaly detection on order data — all in one platform.

**Repository:** github.com/h-enisa/ac-supply-chain-ai

---

## Team

| Member | Project Role | Course Role | Contact |
|--------|-------------|-------------|---------|
| Enisa Halilaj | Team Leader, Repo Master, Documentation | Captain | — |
| Natali Muca | Backend, JWT Authentication | Developer | — |
| Sabina Merkaj | Database, SQLAlchemy Models, Seed Data | Developer | — |
| Alesia Palloshi | Frontend, QA Testing | Tester | — |
| Alesia Gjeta | ML Models, ARIMA Forecasting, Anomaly Detection, ETL | Analyst | — |

### Responsibilities by Role

**Enisa — Captain and Repo Master**
Owns the project timeline, meeting agenda, and milestone tracking. Reviews and merges all pull requests. Enforces branch policy — nothing goes directly to `main`. Resolves merge conflicts in coordination with the relevant developer. Produces architecture documentation, UML diagrams, BPMN, DFD, and ERD. Maintains the GitHub wiki structure and keeps the README current.

**Natali — Backend Developer**
Owns the FastAPI application layer: endpoint routing, request validation, business logic, and JWT authentication. Responsible for all files under `backend/routers/` and `backend/auth/`. API contracts (what each endpoint accepts and returns) must be agreed with the frontend developer before implementation begins.

**Sabina — Database Developer**
Owns the data layer: SQLAlchemy models, database connection setup, and seed scripts. Responsible for `backend/models/` and `backend/database.py`. Any schema change must be communicated to the whole team before it is committed, since it affects every other layer.

**Alesia Palloshi — Frontend Developer and Tester**
Owns the user interface: HTML, JavaScript, Chart.js integration, status badge logic, and responsive layout. Responsible for everything under `frontend/`. Also owns QA for the full system — tests every feature against its acceptance criteria before it is marked done and signs off before any PR targeting production-facing features is merged.

**Alesia Gjeta — ML Developer and Analyst**
Owns the machine learning layer: ARIMA training pipeline, ETL scripts, anomaly detection logic in `ml/inference.py`, and the FastAPI endpoints that serve forecast and anomaly data. Responsible for all files under `ml/`. The interface between `ml/inference.py` and `backend/routers/` must stay import-safe — no circular dependencies.

---

## Communication

**Day-to-day questions and blockers** — WhatsApp group. If something is blocking your work, post it the same day. Do not sit on a blocker for 24 hours.

**Code discussion** — GitHub PR comments. Keep code feedback on the PR so it is visible to the whole team and searchable later.

**Architecture and design decisions** — Weekly meeting. Decisions made over chat are not binding until they are confirmed in a meeting and recorded in the wiki.

**Documentation** — GitHub wiki. Meeting reports, research logs, architecture decisions, and setup guides all live there.

### If Someone Is Not Responding
1. Follow up directly in the WhatsApp group.
2. If no response within 24 hours, raise it at the next meeting.
3. If work is blocked for more than two days, Enisa reassigns or adjusts the scope.

---

## Coding Standards

### Backend (Python / FastAPI)
- Type hints on every function signature — no untyped functions
- Pydantic models for every request and response body
- Google-style docstrings on all public functions
- Custom exception classes for error handling — no bare `except:` blocks
- No raw SQL — use SQLAlchemy ORM for all queries unless Enisa approves an exception
- Functions longer than 50 lines should be refactored

### Frontend (HTML / JavaScript)
- No inline styles — layout and spacing are handled in a shared CSS file
- DOM manipulation through functions, not scattered across script blocks
- `fetch()` calls wrapped with error handling — every request covers the unhappy path
- No `console.log` left in code submitted for review

### Machine Learning (Python)
- ETL steps separated from model training steps — no single script that does both
- Model parameters and thresholds defined as named constants at the top of the file, not as magic numbers inside functions
- Forecast and anomaly outputs serialisable to JSON without manual conversion

### All Code
- No credentials, API keys, or database URLs hardcoded anywhere
- All secrets go in `.env` — which is in `.gitignore` and never committed
- Meaningful variable names — single letters only for loop indices
- Remove debug print statements before submitting a PR

---

## Definition of Done

A feature is not done until all of the following are true.

**Code**
- Follows the standards above
- No unresolved linter errors
- No hardcoded secrets

**Testing**
- Tested manually against the acceptance criteria
- Edge cases covered: empty input, null values, invalid data
- If it is a backend endpoint: tested with both valid and invalid requests
- Alesia Palloshi has signed off for any feature visible in the UI

**Documentation**
- Complex logic has inline comments explaining why, not what
- Any new endpoint is described in a comment above the route function
- Schema changes are communicated to the team and reflected in the ERD

**Review**
- Pull request opened with a clear description of what changed and why
- At least one team member has reviewed and approved
- All review comments resolved
- Enisa has merged — no self-merges

**Integration**
- Feature branch merged to `main` via pull request
- No new merge conflicts introduced

---

## Git Workflow

### Branch Naming
- New features: `feature/natali-auth`, `feature/sabina-models`
- Bug fixes: `fix/forecast-endpoint`, `fix/badge-colours`
- Documentation: `docs/erd-update`, `docs/readme`

### Commit Messages
Use this format:

```
type: short description of what changed

Optional body explaining why the change was made,
or what problem it solves.
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat: add JWT validation middleware to inventory endpoint

fix: correct Low Stock threshold in inventory status logic

docs: update ERD to reflect OrderItem foreign key change
```

### Pull Request Process
1. Push your feature branch to origin
2. Open a PR with a title that describes the change, not the task (write "Add ARIMA forecast endpoint" not "Week 3 work")
3. Add a short description: what you built, how to test it, anything reviewers should know
4. Request review from at least one team member
5. Address all comments before the PR is merged
6. Enisa merges after approval — delete the branch after merge

### Main Branch Rules
- No direct commits to `main` under any circumstances
- Every change goes through a pull request
- At least one approval required before merge
- Enisa is the only person who merges to `main`

---

## File Ownership

Grading is assessed per file. Stay within your designated area unless a change has been discussed and agreed as a team.

| Area | Owner | Files |
|------|-------|-------|
| Backend routing and auth | Natali | `backend/routers/`, `backend/auth/`, `backend/schemas/` |
| Database models and seed | Sabina | `backend/models/`, `backend/database.py`, `backend/seed.py` |
| ML pipeline and inference | Alesia Gjeta | `ml/` |
| Frontend and UI | Alesia Palloshi | `frontend/` |
| Architecture, docs, config | Enisa | `main.py`, `requirements.txt`, `.env.example`, `README.md`, `docs/` |

If a bug in your file is caused by an interface mismatch with another layer, fix it together and note the shared contribution in the PR description.

---

## Meetings

| Type | Schedule | Format | Duration | Run by |
|------|----------|--------|----------|--------|
| Weekly team meeting | Friday, end of day | In person | 1 hour | Enisa |
| Emergency sync | As needed | In person or call | 15 minutes | Enisa |
| PR review discussion | As needed | GitHub or call | 30 minutes | Reviewer |

### Weekly Meeting Format
1. Status round — each member: what is done, what is next, any blockers (15 min)
2. Demo — show something working from the past week (15 min)
3. Blockers and decisions — resolve open questions as a group (15 min)
4. Planning — assign work for the coming week (10 min)
5. Action items — confirm owners and deadlines before leaving (5 min)

Meeting notes are written by Enisa and posted to the wiki within 24 hours.

---

## Decisions and Disagreements

Technical disagreements will happen. When they do:

1. Each side states their position clearly — what they propose and why
2. The team discusses and tries to reach consensus
3. If there is no consensus, Enisa makes the final call
4. The decision is recorded in the meeting report — not just in chat

If the disagreement is about scope, timeline, or something outside the team's control, Enisa escalates to the course instructor.

The rule across all disagreements: critique the idea, not the person.

---

## Security

- `.env` is in `.gitignore` — check before every first commit on a new machine
- `.env.example` lists every required variable with a placeholder value, not the real value
- No passwords, tokens, or database credentials in code, comments, or commit messages
- If a secret is accidentally committed, rotate it immediately and notify Enisa
- The database password and JWT secret key are rotated at the start of each project phase

---

## Quality Targets

| Metric | Target |
|--------|--------|
| PR review turnaround | Under 24 hours |
| Blocker resolution | Under 3 days |
| Missed weekly meetings | Zero |
| Unresolved linter errors at merge | Zero |
| Features merged without Alesia Palloshi QA sign-off | Zero |
| Secrets committed to repository | Zero |

---

*AC Supply Chain AI — Faculty of Information Technology*
*Repository: github.com/h-enisa/ac-supply-chain-ai*
