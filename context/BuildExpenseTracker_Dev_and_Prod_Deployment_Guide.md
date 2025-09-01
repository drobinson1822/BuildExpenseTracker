# BuildExpenseTracker — Deployment Guide for Coding Agent
_Last updated: 2025-09-01 16:02 _

This document provides detailed instructions for deploying **BuildExpenseTracker** into two environments:

- **Development (Dev)**: A safe sandbox where the app can be tested by the builder and close collaborators.  
- **Production (Prod)**: A hardened environment for external testers and eventual real users.

The coding agent should follow these steps exactly, ensuring both environments are isolated and follow best practices.

---

# 0) Context Snapshot

- **Repository**: `drobinson1822/BuildExpenseTracker` (React frontend + FastAPI backend).  
- **Database**: Supabase (Postgres) with Row-Level Security (RLS).  
- **Goal**: Ship a working MVP vertical slice:  
  **Create Project → Add Forecast Line Items → Log Actual Expenses → View Variance & Rollup**  
- **Target Hosting**:  
  - **DB**: Supabase (separate projects for dev & prod).  
  - **Backend**: FastAPI on Render or Fly.io.  
  - **Frontend**: React on Vercel (or Netlify).  
  - **CI/CD**: GitHub Actions (smoke tests + e2e).  

---

# 1) Development Environment Deployment

## 1.1 Supabase (Dev Project)
- Create a Supabase project: `build-expense-tracker-dev`.
- Apply schema migrations (`projects`, `forecast_line_items`, `actual_expenses`, `feedback`).  
- Enable **RLS** on all tables (basic owner-only policies).  
- Create indexes:  
  - `forecast_line_items(project_id)`  
  - `actual_expenses(project_id, date)`
- Add **idempotent seed data**:  
  - 1 Demo Project  
  - 10–15 forecast lines  
  - 8–10 expenses with vendors and dates  
- Toggle seeding with `SEED=true`.

## 1.2 Backend (FastAPI) — Dev Deploy
- Add endpoints:  
  - `GET /healthz` → `{"status":"ok"}`  
  - `GET /version` → git SHA + build timestamp  
- Enforce Supabase JWT auth on **write routes**.  
- Configure **CORS** for:  
  - `http://localhost:*`  
  - Vercel preview domains  
  - `https://app-dev.<your-domain>`  
- Dockerize backend (`uvicorn`) and deploy to Render/Fly.  
- Set env vars from Supabase dev project (`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`).

## 1.3 Frontend (React) — Dev Deploy
- Configure `.env.development` with `VITE_API_BASE_URL=https://api-dev.<your-domain>`.
- Add **“Load Demo Project”** button → loads seeded project by slug/id.  
- Deploy to Vercel (dev project).

## 1.4 Tests — Dev
- **Backend smoke tests**: CRUD happy path for projects, forecast_line_items, actual_expenses.  
- **Frontend e2e** (Playwright): “Create project → add forecast → add expense → view variance.”  
- Run against dev URLs in CI.

## 1.5 Observability — Dev
- Optional: enable Sentry with `environment=dev`.  
- Add `/feedback` endpoint or Supabase table.  
- “Send Feedback” button posts to backend.

## 1.6 Documentation — Dev
- Update `PROJECT_PROGRESS` with:  
  - dev API URL  
  - dev app URL  
  - seed/reset instructions  
  - test flow description  

---

# 2) Production Environment Deployment

## 2.1 Supabase (Prod Project)
- Create a new Supabase project: `build-expense-tracker-prod`.  
- Apply **frozen migrations** from dev.  
- Enable strict **RLS policies** (same as dev but fully audited).  
- Seed only a minimal Demo Project (or none if going live).  
- Apply indexes same as dev.

## 2.2 Backend (FastAPI) — Prod Deploy
- Deploy to Render/Fly with hardened settings:  
  - Enforce HTTPS  
  - Strict CORS: only `https://app.<your-domain>`  
  - Auth required on all writes  
  - Rate-limiting middleware for writes  
- Expose `/healthz`, `/version`.  
- Env vars from prod Supabase project.

## 2.3 Frontend (React) — Prod Deploy
- Configure `.env.production` with `VITE_API_BASE_URL=https://api.<your-domain>`.  
- Deploy to Vercel prod project.  
- Remove “Load Demo” if not needed, or keep one public demo project.

## 2.4 Tests — Prod
- CI must pass smoke tests + e2e before deploy.  
- Separate CI jobs for dev and prod:  
  - `dev` branch → dev deploy  
  - `main` branch → prod deploy

## 2.5 Observability — Prod
- Enable Sentry (`environment=prod`) on both backend and frontend.  
- Feedback mechanism active (writes to Supabase feedback table).  
- Nightly **integrity check** job: recompute rollups and compare against stored totals.  

## 2.6 Rollout Plan
- Start with 3–5 trusted builders and 1 homeowner.  
- Provide them a single flow to test:  
  **“Create project, add 10 forecast lines, log 5 expenses.”**  
- Gather feedback via button + short call.  
- Iterate before wider rollout.

---

# 3) CI/CD Setup (Both Environments)

- **Branching**:  
  - `dev` branch → auto-deploy to dev environment  
  - `main` branch → auto-deploy to prod environment  

- **GitHub Actions Workflows**:  
  - **Backend workflow**: install → pytest → build Docker → deploy to Render/Fly.  
  - **Frontend workflow**: npm ci → build → run Playwright → deploy to Vercel.  
  - PRs: run smoke + e2e; deploy Preview builds.  

---

# 4) Execution Order Summary

## Dev Deployment
1. Provision Supabase dev project + seed data (🔴 High)  
2. Configure backend env + deploy API (🔴 High)  
3. Configure frontend env + deploy UI (🔴 High)  
4. Add health/version + JWT + CORS (🔴 High)  
5. Write smoke/e2e tests (🟠 Medium)  
6. Hook into CI (🟠 Medium)  
7. Add optional observability/feedback (🟡 Medium)

## Prod Deployment
1. Freeze schema/migrations from dev (🔴 High)  
2. Provision Supabase prod project (🔴 High)  
3. Deploy backend with hardened CORS/auth (🔴 High)  
4. Deploy frontend prod build (🔴 High)  
5. Require tests pass in CI before deploy (🟠 Medium)  
6. Enable Sentry + feedback pipe (🟠 Medium)  
7. Nightly data integrity check (🟡 Medium)  
8. Controlled rollout to pilot users (🟡 Medium)

---

# 5) Hand-off Notes for the Coding Agent

- Treat **Dev** as the proving ground. You can reset seed data freely and adjust RLS minimally.  
- Treat **Prod** as stable: freeze migrations, lock CORS/auth, no demo resets.  
- Always confirm secrets are not in the frontend bundle.  
- Commits should be small, with PRs referencing which step from this guide they cover.  
- Document any deviations in a `Findings` section at the top of this file.

---

End of Deployment Guide.
