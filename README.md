# BuildExpenseTracker

A modern web application for forecasting, budgeting, and tracking expenses throughout a construction or home build project.

---

## Overview

**BuildExpenseTracker** is a full-stack MVP that enables users to:
- Create and manage multiple construction projects
- Define detailed forecast (budget) line items for each project
- Log and track actual expenses against each forecast item
- Visualize progress, compare estimated vs. actual costs, and monitor draw readiness

The app is designed for single-user/internal use (no authentication required for MVP) and is optimized for fast, spreadsheet-like entry and editing of budget data.

---

## Features

- **Project Management:**
  - Add/view multiple projects with address, dates, status, and square footage
- **Forecast/Budget Table:**
  - Excel-like, editable table of forecast line items per project
  - Add, edit, and update category, description, estimated cost, progress, and status
  - See estimated vs. actuals side by side for each line item
- **Expense Tracking:**
  - Log actual expenses, link to forecast items, and track vendor, date, amount, and receipts
- **Progress & Dashboard (Planned):**
  - Visualize project status, budget vs. actuals, and draw readiness
- **Modern Tech Stack:**
  - React (Vite) frontend, Tailwind CSS UI
  - FastAPI backend (Python), SQLAlchemy ORM
  - SQLite for local/dev, easy migration to Postgres/Supabase for production

---

## Architecture

```
frontend/   # React + Tailwind (Vite)
backend/    # FastAPI, SQLAlchemy, Pydantic, SQLite
```

- **API:** RESTful endpoints for projects, forecast line items, expenses, and draws
- **Database:**
  - `Project`, `ForecastLineItem`, `ActualExpense`, `DrawTracker` tables
  - Designed for easy migration from SQLite (dev) to Postgres (prod)

---

## Quickstart

### Prerequisites
- Python 3.9+
- Node.js (v18+ recommended)

### 1. Backend (FastAPI)

```sh
cd backend
pip install -r requirements.txt  # Or: python3 -m pip install -r requirements.txt
uvicorn main:app --reload
```
- By default uses SQLite (set `DATABASE_URL` in `.env` to override)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend (React)

```sh
cd frontend
npm install
npm run dev
```
- App runs at [http://localhost:5173](http://localhost:5173)
- Connects to backend at `http://localhost:8000`

---

## Usage

1. **Create a Project:**
   - Enter name, address, dates, status, and total sqft
2. **Add Forecast Line Items:**
   - Use the compact table to add/edit categories, costs, units, notes, progress, and status
   - Inline editing for rapid workflow
3. **Log Expenses:**
   - Add expenses, link to forecast items, and upload receipts (planned)
4. **Monitor Progress:**
   - Compare estimated vs. actual costs for each line item
   - Dashboard and draw readiness (coming soon)

---

## Development Notes

- **No authentication** in MVP; intended for single-user/internal use
- All backend endpoints are fully tested (see `backend/test_api.py`)
- Modernized for SQLAlchemy 2.x and Pydantic v2
- Designed for easy extension (add authentication, dashboards, deployment)

---

## Roadmap
- [ ] Dashboard view for overall budget/progress
- [ ] Draw readiness and payment tracking
- [ ] User authentication (optional)
- [ ] Production deployment (Supabase/Postgres + Vercel/Render)

---

## License
MIT
