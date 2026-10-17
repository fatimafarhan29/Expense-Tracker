# PLAN.md — Smart Expense Tracker

Phased build plan for the Smart Expense Tracker (Python + Streamlit + Neon PostgreSQL).
Each phase lists what changes and how to verify it.

**Stack decisions (confirmed with project owner):**
- UI: Python + Streamlit (free)
- Storage: Neon serverless PostgreSQL, free tier (expenses **and** budgets) — internet required
- CSV: export-only feature (download of the filtered view; no local data file)
- Testing: manual checklist (`TESTING.md`) — free local tools only
- All packages free/open-source: streamlit, pandas, plotly, psycopg2-binary, python-dotenv

---

## Phase 1 — Project Structure & Setup ✅

**Changes:** Create file skeleton — `requirements.txt` (5 free packages), `.gitignore` (excludes `.env`, `streamlit_log.txt`, caches), `.env.example` template, minimal `app.py` (title page only), `agent.md` governing all later work.

**Verify:**
- `pip install -r requirements.txt` completes; all imports succeed
- `python -m py_compile app.py` passes
- `streamlit run app.py` serves http://localhost:8501 with the app title, no errors

## Phase 2 — Database Layer (Neon) ✅

**Changes:** `database.py` — `get_connection()`, `ensure_tables()`, `get_expenses()`, `add_expense()`, `delete_expense()`, `get_budget()`, `set_budget()`. All parameterized queries; connection string read from `.env` (`NEON_DATABASE_URL`) via python-dotenv; friendly errors on failure. Fixed schema: `expenses(id, date, description, category, amount, created_at)` and `budgets(month PK, amount)`.

**Verify:**
- `ensure_tables()` connects to Neon; `information_schema.tables` shows `['budgets', 'expenses']`
- CRUD round-trip: insert test row → appears in Neon SQL Editor → delete → gone

## Phase 3 — UI: Add, List & Delete ✅

**Changes:** `app.py` — sidebar form (date picker, description, category selectbox, amount > 0), expense table, per-row delete buttons, success/error messages via session-state flash, empty-state message, DB errors shown via `st.error` (never a traceback).

**Verify:**
- Add expense → appears in table **and** in Neon; refresh → persists
- Delete → removed from both; empty description → friendly error
- Headless `AppTest` run: no exceptions, form submission lands row in DB

## Phase 4 — Dashboard: Metrics & Charts ✅

**Changes:** Metric row (total spent, count, average, top category) + plotly donut (spending by category) and bar chart (spending by month). All computed from the already-loaded DataFrame — no extra DB queries.

**Verify:**
- Seed known amounts (e.g. Food $10 + Transport $20) → metrics exactly $30.00 / 2 / $15.00 / Transport
- Charts render; adding data updates them immediately

## Phase 5 — Budget, Filters & CSV Export ✅

**Changes:**
- Monthly budget UI: month selectbox, budget input (prefilled from DB), Save → `set_budget()` upsert; `st.progress` bar with ≥80% warning and over-budget error (uses unfiltered monthly totals)
- Sidebar filters: date range, category multiselect, amount slider — AND logic; drives metrics, charts, table, delete list, and export; "Showing X of Y" caption; no-match warning
- `st.download_button` → `expenses_filtered.csv` generated in memory from the filtered view

**Verify:**
- Budget 100 with 250 spent → over-budget error; reload → saved budget restored
- Each filter narrows table + metrics + export together; combined filters intersect
- Downloaded CSV contains exactly the filtered rows

## Phase 6 — Testing & Polish ✅

**Changes:** `TESTING.md` (manual checklist: every feature + edge cases — empty description, delete-last-row, over-budget, no-match filters, special characters, long text, `.env` renamed, narrow window, restart persistence), `README.md` (setup with Neon steps), final docstring/layout polish.

**Verify:** Walk `TESTING.md` end-to-end in the browser; every box ticked = done.

---

## Current status

- All 6 phases built and verified (automated checks passed; DB round-trips confirmed against the real Neon database; test data cleaned up)
- Run: `streamlit run app.py` → http://localhost:8501
- Remaining owner task: walk `TESTING.md` visually in the browser

## Known environment issue — RESOLVED

**Symptom:** browser showed a blank page / `ERR_CONNECTION_REFUSED` while development seemed complete.

**Root cause (two combined factors):**
1. Background Streamlit servers launched during development kept being killed by shell-session teardowns — the browser lost its live WebSocket and rendered a blank page (or refused entirely once nothing was listening on 8501).
2. The project's `.venv` (auto-activated by VS Code) had **no packages installed** — installs had gone to system Python — so `streamlit run app.py` failed in the owner's terminal ("streamlit not found"), preventing them from running their own stable server.

**Fixes applied:**
- Installed `requirements.txt` into `.venv` (streamlit 1.66.0 + deps verified by import)
- Server restarted from the venv; health endpoint returns `ok`
- Owner confirmed: **app is working in the browser**

**Lesson for this project:** run the app from the owner's own VS Code terminal (`streamlit run app.py`, venv auto-activates) rather than from agent background processes — the terminal stays alive as long as the user keeps it open.
