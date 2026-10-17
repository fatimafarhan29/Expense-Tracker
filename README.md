# 💰 Smart Expense Tracker

A beginner-friendly personal expense tracker built with **Python** and **Streamlit**.
Data is stored in a serverless **PostgreSQL** database on the free tier of
[Neon](https://neon.tech), with CSV export for downloading your records.

## Features

- ➕ Add, list, and delete expenses — persisted in Neon PostgreSQL
- 📊 Dashboard: total spent, expense count, average, top category
- 📈 Charts: spending by category (donut) and by month (bar), via plotly
- 💰 Monthly budget with a live progress bar — budgets saved per month in the database
- 🔍 Filters: date range, categories, amount range (drive the whole page)
- ⬇️ CSV export of the currently filtered view (generated in memory)

## Prerequisites

- Python 3.10 or newer
- A free account at [neon.tech](https://neon.tech) (free tier only)

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the database connection:**

   - Copy `.env.example` to `.env`
   - In the Neon Console: your project → **Connection Details** → copy the `postgresql://…` URL
   - Paste it into `.env` as:

     ```
     NEON_DATABASE_URL=postgresql://your-real-connection-string
     ```

   > ⚠️ `.env` contains a secret. It is git-ignored — never commit it or share it.

3. **Run the app:**

   ```bash
   streamlit run app.py
   ```

   Open http://localhost:8501 in your browser. The `expenses` and `budgets`
   tables are created automatically on first run.

## Project structure

```
smart-expense-tracker/
├── agent.md               # Project instructions & rules for AI/dev work
├── app.py                 # Streamlit UI: form, dashboard, budget, filters, export
├── database.py            # Neon/PostgreSQL data layer (all SQL lives here)
├── .env                   # Your real connection string (NEVER commit)
├── .env.example           # Safe template showing the required variable
├── .gitignore             # Keeps .env, logs, and caches out of git
├── requirements.txt       # streamlit, pandas, plotly, psycopg2-binary, python-dotenv
├── TESTING.md             # Manual testing checklist
└── README.md              # This file
```

## Tech stack (all free)

| Purpose | Tool |
|---|---|
| Language | Python 3.10+ |
| UI | Streamlit |
| Database | Neon PostgreSQL (free tier) |
| DB driver | psycopg2-binary |
| Data handling | pandas |
| Charts | plotly |
| Config | python-dotenv |

## Testing

See [TESTING.md](TESTING.md) for the full manual checklist — walk it end-to-end
after any significant change.

## Data model

- `expenses` — id, date, description, category, amount, created_at
- `budgets` — month (`YYYY-MM`), amount

Full schema and coding rules: [agent.md](agent.md).
