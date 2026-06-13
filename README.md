# EnCash

**Personal finance, simplified.** EnCash ingests messy real-world financial
data, normalizes it into a clean transaction ledger, and surfaces simple,
secure analytics through a dashboard.

This is the **MVP**: it takes one data source — **bank SMS transaction alerts** —
all the way through the pipeline (ingest → parse → normalize → categorize →
dedup → store → analyze → visualize). The parser layer sits behind a single
interface so PDF and Excel parsers can be added later without changing the
pipeline.

## Architecture

```
Browser (React dashboard)
        │  HTTPS / JWT (Authorization: Bearer)
        ▼
Django + DRF  ── ingest/parsers (SMS now; PDF/Excel later, same interface)
        │          ingest/services (normalize, categorize, dedup, pipeline)
        ▼
PostgreSQL (per-user transactions, categories, users)
```

- **Backend:** Django 5 + Django REST Framework, chosen for its secure-by-default
  posture (CSRF/XSS/SQLi/clickjacking protection, mature auth/permissions, ORM).
- **Auth:** JWT access + refresh tokens (`djangorestframework-simplejwt`) with
  rotation and logout blacklisting. argon2 password hashing.
- **Frontend:** React (Vite + TypeScript) with Recharts.
- **DB:** PostgreSQL in production; SQLite for local dev/tests.

## Security highlights

- argon2 password hashing; password-strength validators.
- Short-lived JWT access tokens, rotating refresh tokens, blacklist on logout.
- Strict **per-user data isolation** on every query (see `get_queryset`).
- DRF throttling on auth (`10/min`) and ingest (`20/min`) endpoints.
- CORS locked to the dashboard origin; ORM-only queries; serializer validation
  on all untrusted input; secrets via environment variables.
- Production settings enable HSTS, secure cookies, and other `SECURE_*` headers.
- Audit logging of auth/ingest events without logging financial values.

## Project layout

```
backend/    Django project (accounts, transactions, ingest, analytics)
frontend/   React dashboard (Vite + TypeScript + Recharts)
docker-compose.yml   db + backend + frontend
```

## Run it

### Option A — Docker (full stack)

```bash
cp .env.example .env          # set DJANGO_SECRET_KEY at minimum
docker compose up --build
# Dashboard: http://localhost:8080
```

### Option B — Local development

Backend (SQLite by default, no DB server needed):

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate          # also seeds default categories
python manage.py runserver        # http://localhost:8000
```

Frontend (proxies /api to the backend on :8000):

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

## API overview

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| POST | `/api/auth/register/` | Create an account |
| POST | `/api/auth/token/` | Obtain access + refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh the access token |
| POST | `/api/auth/logout/` | Blacklist a refresh token |
| GET  | `/api/auth/me/` | Current user |
| POST | `/api/ingest/sms/` | Ingest a block of SMS alerts |
| GET  | `/api/transactions/` | List/filter transactions |
| PATCH| `/api/transactions/{id}/` | Re-categorize a transaction |
| GET  | `/api/categories/` | List/create categories |
| GET  | `/api/analytics/summary/` | Income / expense / net / count |
| GET  | `/api/analytics/by-category/` | Spend grouped by category |
| GET  | `/api/analytics/trend/` | Monthly income vs. expense |
| GET  | `/api/analytics/top-merchants/` | Top expense merchants |

Analytics endpoints accept optional `date_from` / `date_to` (`YYYY-MM-DD`).

## Tests

```bash
cd backend
python -m pytest          # parser, services, API, isolation, throttling
```

## Roadmap (post-MVP)

PDF statement parsing & OCR, Excel/CSV import, TOTP/MFA, ML/LLM categorization,
recurring-subscription detection, budgets/goals, multi-currency, column-level
encryption.
