"""Neon PostgreSQL data layer for the Smart Expense Tracker.

Every function opens a short-lived connection, does one job, and closes it.
All queries are parameterized (values passed as tuples, never string-built)
per the rules in agent.md. Requires NEON_DATABASE_URL in the local .env file.
"""

import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Read .env into environment variables once, at import time

EXPENSES_DDL = """
    CREATE TABLE IF NOT EXISTS expenses (
        id          SERIAL PRIMARY KEY,
        date        DATE          NOT NULL,
        description TEXT          NOT NULL,
        category    TEXT          NOT NULL,
        amount      NUMERIC(10,2) NOT NULL CHECK (amount > 0),
        created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
    )
"""

BUDGETS_DDL = """
    CREATE TABLE IF NOT EXISTS budgets (
        month  TEXT PRIMARY KEY,
        amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0)
    )
"""


def get_connection():
    """Open a new connection to Neon.

    Reads NEON_DATABASE_URL from the environment (.env file, local runs)
    or from Streamlit secrets (deployed apps, e.g. Streamlit Community Cloud).

    Returns:
        psycopg2 connection object.

    Raises:
        RuntimeError: if no connection string is configured in either place.
    """
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        # Deployed on Streamlit Community Cloud: the value lives in secrets.
        try:
            import streamlit as st

            db_url = st.secrets.get("NEON_DATABASE_URL")
        except Exception:
            db_url = None
    if not db_url:
        raise RuntimeError(
            "NEON_DATABASE_URL is not set. Locally: add it to a .env file. "
            "On Streamlit Cloud: add it under Settings -> Secrets."
        )
    return psycopg2.connect(db_url)


def ensure_tables():
    """Create the expenses and budgets tables if they do not exist (safe to rerun)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(EXPENSES_DDL)
            cur.execute(BUDGETS_DDL)
        conn.commit()
    finally:
        conn.close()


def get_expenses() -> pd.DataFrame:
    """Return every expense, newest date first.

    Returns:
        DataFrame with columns: id, date, description, category, amount, created_at.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, date, description, category, amount, created_at "
                "FROM expenses ORDER BY date DESC, id DESC"
            )
            rows = cur.fetchall()
            columns = [col.name for col in cur.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


def add_expense(date: str, description: str, category: str, amount: float) -> None:
    """Insert one expense row.

    Args:
        date: ISO date string 'YYYY-MM-DD'.
        description: short text describing the expense.
        category: one of the app's fixed category names.
        amount: positive number with at most 2 decimals.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO expenses (date, description, category, amount) "
                "VALUES (%s, %s, %s, %s)",
                (date, description, category, amount),
            )
        conn.commit()
    finally:
        conn.close()


def delete_expense(expense_id: int) -> None:
    """Delete one expense by its id. No error if the id does not exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
    finally:
        conn.close()


def get_budget(month: str):
    """Return the budget set for a 'YYYY-MM' month, or None if none exists.

    Args:
        month: calendar month as 'YYYY-MM', e.g. '2026-10'.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT amount FROM budgets WHERE month = %s", (month,))
            row = cur.fetchone()
        return float(row[0]) if row else None
    finally:
        conn.close()


def set_budget(month: str, amount: float) -> None:
    """Insert or update the budget for a 'YYYY-MM' month.

    Args:
        month: calendar month as 'YYYY-MM', e.g. '2026-10'.
        amount: non-negative budget value.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO budgets (month, amount) VALUES (%s, %s) "
                "ON CONFLICT (month) DO UPDATE SET amount = EXCLUDED.amount",
                (month, amount),
            )
        conn.commit()
    finally:
        conn.close()
