"""Smart Expense Tracker — Streamlit entry point (final: full feature set).

Features: add/list/delete expenses, dashboard metrics + charts, monthly budget
with progress bar, filters (date/category/amount), and CSV export.
Data layer: database.py -> Neon PostgreSQL. Setup: see README.md.
"""

from datetime import date

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

import database

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Travel",
    "Other",
]

st.set_page_config(page_title="Smart Expense Tracker", page_icon="💰", layout="wide")
st.title("💰 Smart Expense Tracker")

# Flash message survives the st.rerun() triggered by add/delete actions.
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

# Create tables on first run (idempotent, per agent.md).
try:
    database.ensure_tables()
except (psycopg2.Error, RuntimeError) as exc:
    st.error(f"Could not connect to the database: {exc}")
    st.stop()

# ---------- Sidebar: add expense form ----------
with st.sidebar:
    st.header("➕ Add expense")
    with st.form("add_expense_form", clear_on_submit=True):
        expense_date = st.date_input("Date", value=date.today())
        description = st.text_input("Description", placeholder="e.g. Coffee")
        category = st.selectbox("Category", CATEGORIES)
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Add expense", use_container_width=True)

    if submitted:
        if not description.strip():
            st.error("Description cannot be empty.")
        else:
            try:
                database.add_expense(
                    expense_date.isoformat(),
                    description.strip(),
                    category,
                    float(amount),
                )
                st.session_state["flash"] = "✅ Expense added."
                st.rerun()
            except (psycopg2.Error, RuntimeError) as exc:
                st.error(f"Could not save the expense: {exc}")

# ---------- Load data ----------
try:
    expenses = database.get_expenses()
except (psycopg2.Error, RuntimeError) as exc:
    st.error(f"Could not load expenses: {exc}")
    st.stop()

if not expenses.empty:
    expenses["amount"] = expenses["amount"].astype(float)
    expenses["date"] = pd.to_datetime(expenses["date"])
    expenses["month"] = expenses["date"].dt.strftime("%Y-%m")

# ---------- Sidebar: filters (Phase 5) ----------
view = expenses
if not expenses.empty:
    with st.sidebar:
        st.header("🔍 Filters")
        min_date = expenses["date"].min().date()
        max_date = expenses["date"].max().date()
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        all_categories = sorted(expenses["category"].unique())
        selected_categories = st.multiselect(
            "Categories", all_categories, default=all_categories
        )
        max_amount = float(expenses["amount"].max())
        amount_range = st.slider("Amount ($)", 0.0, max_amount, (0.0, max_amount))

    mask = pd.Series(True, index=expenses.index)
    if len(date_range) == 2:
        mask &= expenses["date"].between(
            pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        )
    elif len(date_range) == 1:
        mask &= expenses["date"].dt.normalize() == pd.Timestamp(date_range[0])
    mask &= expenses["category"].isin(selected_categories)
    mask &= expenses["amount"].between(amount_range[0], amount_range[1])
    view = expenses[mask]

# ---------- Monthly budget (Phase 5) ----------
st.subheader("💰 Monthly budget")
current_month = date.today().strftime("%Y-%m")
months = sorted(expenses["month"].unique()) if not expenses.empty else []
if current_month not in months:
    months = [current_month, *months]
budget_month = st.selectbox("Month", months, key="budget_month")

try:
    saved_budget = database.get_budget(budget_month)
except (psycopg2.Error, RuntimeError) as exc:
    st.error(f"Could not load the budget: {exc}")
    saved_budget = None

b1, b2 = st.columns([3, 1])
with b1:
    budget_value = st.number_input(
        "Budget ($)",
        min_value=0.0,
        step=10.0,
        value=saved_budget if saved_budget is not None else 0.0,
        key=f"budget_input_{budget_month}",
    )
with b2:
    st.write("")  # spacer for vertical alignment
    if st.button("Save budget", use_container_width=True, key="save_budget"):
        try:
            database.set_budget(budget_month, float(budget_value))
            st.session_state["flash"] = f"💰 Budget for {budget_month} saved."
            st.rerun()
        except (psycopg2.Error, RuntimeError) as exc:
            st.error(f"Could not save the budget: {exc}")

spent_this_month = (
    float(expenses.loc[expenses["month"] == budget_month, "amount"].sum())
    if not expenses.empty
    else 0.0
)
if budget_value > 0:
    ratio = spent_this_month / budget_value
    st.progress(
        min(ratio, 1.0),
        text=f"${spent_this_month:,.2f} of ${budget_value:,.2f} spent ({ratio:.0%})",
    )
    if ratio > 1:
        st.error(f"⚠️ Over budget by ${spent_this_month - budget_value:,.2f}!")
    elif ratio >= 0.8:
        st.warning("⚠️ Close to your budget limit.")
else:
    st.caption(
        f"Spent in {budget_month}: ${spent_this_month:,.2f}. "
        "Enter a budget above and press Save to start tracking."
    )

# ---------- Dashboard / table (filtered view) ----------
if expenses.empty:
    st.info("No expenses yet — add your first one with the form in the sidebar.")
elif view.empty:
    st.warning("No expenses match the current filters.")
else:
    display = view.copy()
    st.caption(f"Showing {len(view)} of {len(expenses)} expenses")

    # ---------- Dashboard: summary metrics ----------
    st.subheader("📊 Dashboard")
    total = display["amount"].sum()
    count = len(display)
    average = total / count
    by_category = (
        display.groupby("category")["amount"].sum().sort_values(ascending=False)
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total spent", f"${total:,.2f}")
    m2.metric("Expenses", f"{count}")
    m3.metric("Average expense", f"${average:,.2f}")
    m4.metric("Top category", by_category.index[0], f"${by_category.iloc[0]:,.2f}")

    # ---------- Dashboard: charts ----------
    chart_left, chart_right = st.columns(2)

    with chart_left:
        pie_df = by_category.reset_index()
        pie_df.columns = ["category", "amount"]
        fig_pie = px.pie(
            pie_df,
            names="category",
            values="amount",
            hole=0.4,
            title="Spending by category",
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_right:
        by_month = display.groupby("month")["amount"].sum().reset_index()
        fig_bar = px.bar(
            by_month,
            x="month",
            y="amount",
            title="Spending by month",
            labels={"month": "Month", "amount": "Amount ($)"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ---------- All expenses ----------
    st.subheader("All expenses")
    st.dataframe(display.drop(columns=["month"]), use_container_width=True, hide_index=True)

    # ---------- CSV export (Phase 5) ----------
    st.subheader("⬇️ Export")
    st.download_button(
        "Download filtered expenses as CSV",
        data=display.drop(columns=["month"]).to_csv(index=False),
        file_name="expenses_filtered.csv",
        mime="text/csv",
    )

    st.subheader("🗑️ Delete an expense")
    for _, row in display.iterrows():
        cols = st.columns([4, 3, 1])
        cols[0].write(f"**{row['description']}** · {row['category']}")
        cols[1].write(f"{row['date']} · ${row['amount']:.2f}")
        if cols[2].button("Delete", key=f"del_{int(row['id'])}"):
            try:
                database.delete_expense(int(row["id"]))
                st.session_state["flash"] = (
                    f"🗑️ Deleted “{row['description']}” (${row['amount']:.2f})."
                )
                st.rerun()
            except (psycopg2.Error, RuntimeError) as exc:
                st.error(f"Could not delete the expense: {exc}")

