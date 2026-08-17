# LearnFlow

An AI-training course platform: catalog, course detail, lesson player, quizzes,
learner progress dashboard, and an instructor course builder + analytics —
implemented from the [design prototype](https://claude.ai/design) against the
authentication requirements in `learnflow1-auth-brd.md`.

- **Backend:** FastAPI + SQLAlchemy (async) + PostgreSQL 17 + JWT auth
- **Frontend:** React 19 + TypeScript + Vite + React Router

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop (for PostgreSQL)

## 1. Database

```bash
docker compose up -d db
```

Starts PostgreSQL 17 on `localhost:5432` (user/db `learnflow` / password `learnflow`).

## 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

copy .env.example .env            # then fill in real SMTP credentials
alembic upgrade head
python -m app.seed                # seeds 12 demo courses + demo accounts

uvicorn app.main:app --reload --port 8000
```

Demo accounts created by the seed script (printed to the console too):

| Role       | Email                       | Password             |
|------------|------------------------------|-----------------------|
| Learner    | `learner@learnflow.dev`      | `LearnFlowDemo!2026`  |
| Instructor | `instructor@learnflow.dev`   | `LearnFlowDemo!2026`  |

### Email

Registration, verification, password reset, and account-notification emails
are sent over real SMTP — set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
`SMTP_PASSWORD`, `SMTP_FROM` in `backend/.env` to your provider's credentials
(any standard SMTP provider works: Gmail, SendGrid, Mailgun, SES, etc.).

For local development without real credentials, point `SMTP_HOST`/`SMTP_PORT`
at a local debug catcher instead of a real provider:

```bash
pip install aiosmtpd
python -m aiosmtpd -n -l localhost:1025
```

and set `SMTP_HOST=localhost`, `SMTP_PORT=1025`, `SMTP_USE_TLS=false` — every
verification/reset link will print to that terminal instead of being delivered.

## 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env            # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

Visit `http://localhost:5173`.

## Architecture notes

- **Auth**: 15-minute JWT access tokens (returned in the response body, held
  in memory client-side) + 7-day opaque refresh tokens (`HttpOnly`, `Secure`,
  `SameSite=Strict` cookie, rotated on every use). Reusing an already-rotated
  refresh token revokes the entire token family (theft detection). Two
  concurrent refresh calls are single-flighted client-side
  (`frontend/src/lib/api.ts`) rather than handled with a server-side grace
  window.
- **Passwords**: Argon2 hashing, NFKC normalization, a curated local
  common-password list (`backend/app/security/common_passwords.txt`) — this
  approximates but does not replace a live breach-database lookup (e.g. Have
  I Been Pwned's k-anonymity API); swap it in before relying on this for real
  users.
- **Rate limiting / lockout**: `slowapi` (in-process, per-IP) on
  register/login/forgot-password, plus a per-account failed-attempt counter
  and 15-minute lockout (BR-5). The in-process limiter is fine for a single
  instance; a multi-instance deployment needs a shared store (e.g. Redis).
- **Email delivery**: dispatched from a FastAPI `BackgroundTask` with a small
  retry-with-backoff wrapper, not a durable queue — a process restart mid-send
  can lose a message. Acceptable here; swap in Celery/SQS-backed delivery
  before production scale.
- **Ownership model**: instructors only see and edit their own courses ("My
  courses" / analytics are scoped to `instructor_id`). This is a deliberate
  improvement over the design prototype, which showed every course to every
  instructor (a single-user demo shortcut, not real multi-tenant behavior).
- **Roles**: `learner`, `instructor`, `administrator` are modeled end-to-end
  (registration only allows the first two), but no admin UI is built — the
  design project doesn't include one. Role changes take effect on next token
  refresh, not mid-session (EC-T-09).
