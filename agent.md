# AGENT.md — Smart Expense Tracker

Instructions for AI agents and developers working on this project.
Read this file before making any changes.

---

## 1. Project Goals

- Build a **beginner-friendly frontend project**: a personal Smart Expense Tracker.
- UI framework: **Python + Streamlit** (single-page app, runs locally in the browser).
- Primary data storage: **Neon serverless PostgreSQL (free tier)** — a real relational database; data persists across sessions.
- **CSV is only an export feature** — the download button builds a CSV in memory from the current view; no local data file is required.
- **Free tools only** — Neon free tier + open-source libraries; no paid services or paid API subscriptions. An internet connection is required for the database.
- Code must stay simple and readable so a beginner can understand every line.

## 2. Required Features

The app MUST include all of the following:

1. **Add expense** — form with date, description, category, and amount (validated: amount > 0).
2. **List expenses** — table of all records, friendly empty-state message when no data.
3. **Delete expense** — remove a record; data persists after deletion.
4. **Summary metrics** — total spent, expense count, average expense, top category.
5. **Dashboard charts** — spending by category (pie/bar) and monthly trend (line/bar).
6. **Budget tracking** — set a monthly budget, show a progress bar of spent vs. budget; budgets are saved per month (`YYYY-MM`) in the Neon `budgets` table.
7. **Filters / search** — filter by date range, category (multiselect), and amount range.
8. **CSV export** — download button that exports the currently filtered view as a CSV (generated in memory, no local file).
9. **Persistence** — every add/delete is written immediately to the **Neon PostgreSQL** `expenses` table.

### Database schema (Neon PostgreSQL — fixed; do not change without updating all code)

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id          SERIAL PRIMARY KEY,
    date        DATE        NOT NULL,
    description TEXT        NOT NULL,
    category    TEXT        NOT NULL,
    amount      NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Budgets are stored per calendar month:

```sql
CREATE TABLE IF NOT EXISTS budgets (
    month  TEXT PRIMARY KEY,          -- calendar month as YYYY-MM
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0)
);
```

- `date` — ISO format `YYYY-MM-DD`; `amount` — positive decimal, max 2 decimal places.
- Both tables are auto-created on first run if they do not exist.
- **Connection string** lives in `.env` as `NEON_DATABASE_URL` — never hard-code it, never commit `.env`.

## 3. Coding Rules

- **Python 3.10+** and **Streamlit** only for the UI. Use `pandas` for data handling, `plotly` for charts, `psycopg2` (binary) for PostgreSQL, and `python-dotenv` to load the connection string (all free/open-source).
- **Separate data logic from UI**: all SQL/database operations go in `database.py` as small functions (`get_expenses`, `add_expense`, `delete_expense`, `get_budget`, `set_budget`, `ensure_tables`); `app.py` contains only layout and widget calls.
- **Always use parameterized queries** (`cursor.execute("... WHERE id = %s", (expense_id,))`) — never f-strings or `%` formatting to inject values into SQL.
- **Never hard-code the connection string** — read `NEON_DATABASE_URL` from `.env` via `python-dotenv`. Never commit `.env`.
- One function = one job, max ~30 lines. Use meaningful names (`add_expense`, not `add_data`).
- Every function gets a short docstring explaining purpose, parameters, and return value.
- **Validate inputs** before writing: positive amount, valid date, non-empty description. Show errors with `st.error(...)`, never crash with a traceback.
- Handle edge cases: database unreachable (show a friendly `st.error`, never a traceback), empty result set, deleting the last row, special characters in descriptions (parameterized queries handle this), missing `.env` file.
- Never commit secrets or API keys — this project needs none.
- Keep imports at the top; no commented-out dead code; no `print()` debugging in the final app (use `st.write` only while actively debugging, then remove).
- Follow PEP 8 (4-space indent, snake_case names).

## 4. Project Structure

```
smart-expense-tracker/
├── agent.md               # This file — project instructions (do not delete)
├── app.py                 # Streamlit entry point: layout, widgets, charts
├── database.py            # Neon/PostgreSQL data layer: connection + SQL functions
├── .env                   # NEON_DATABASE_URL connection string (NEVER commit)
├── .env.example           # Template showing required env vars (safe to commit)
├── .gitignore             # Ignores .env, __pycache__, etc.
├── requirements.txt       # Free dependencies: streamlit, pandas, plotly, psycopg2-binary, python-dotenv
├── TESTING.md             # Manual testing checklist (Phase 6)
└── README.md              # How to install, configure .env, and run the app
```

### Setup (one time)

1. Create a free account at [neon.tech](https://neon.tech) and create a project (free tier).
2. Copy the connection string (looks like `postgresql://user:password@host/db?sslmode=require`).
3. Create a `.env` file in the project root:
   ```
   NEON_DATABASE_URL=postgresql://user:password@host/db?sslmode=require
   ```
4. Install and run from the project root:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 5. Free Tools Only

Everything used in this project must be free (no paid plans):

| Purpose | Tool (all free) |
|---|---|
| Language | Python 3.10+ (python.org) |
| Package install | pip |
| UI framework | Streamlit |
| Database | Neon PostgreSQL — free tier (cloud, requires internet + free account) |
| DB driver | psycopg2-binary |
| Env config | python-dotenv |
| Data handling | pandas |
| Charts | plotly (open-source) |
| Editor | VS Code (free edition) |
| Version control | Git (local repos only) |
| Testing | Manual checklist in `TESTING.md` |

**Rules:**

- ❌ No paid cloud hosting, premium APIs, paid database tiers, or subscription services.
- ✅ Neon **free tier only** — do not enable paid add-ons; the app must work within free limits.
- ✅ All Python packages are open-source and installed with: `pip install -r requirements.txt`
- ✅ Connection string stays in `.env` (git-ignored) — never in code, never committed.
- ✅ Verification is done by running the app locally and walking through `TESTING.md`.

## 6. Development Workflow

1. Read this file (`agent.md`) before any change.
2. Work on one phase at a time (see project plan: structure → data layer → UI → dashboard → budget/filters → testing).
3. After each change: save, rerun `streamlit run app.py`, and verify in the browser.
4. Finish by completing every item in the `TESTING.md` manual checklist.
