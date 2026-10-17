# TESTING.md — Manual Testing Checklist

Walk through every item below with the app running (`streamlit run app.py`).
Tick each box when it passes. If any item fails, note it and fix before moving on.

## 1. Setup & first load

- [ ] `pip install -r requirements.txt` completes without errors
- [ ] `streamlit run app.py` opens http://localhost:8501 with no errors in the terminal
- [ ] Title **"💰 Smart Expense Tracker"** is visible
- [ ] With an empty database: info message "No expenses yet — add your first one with the form in the sidebar." appears
- [ ] "💰 Monthly budget" section is visible with the current month selected

## 2. Add expenses

- [ ] Sidebar form shows Date (today), Description, Category (9 options), Amount (cannot go below 0.01)
- [ ] Add *Coffee · Food · 4.50 · today* → green "✅ Expense added." message
- [ ] The expense appears in the table immediately
- [ ] Add *Bus fare · Transport · 2.75 · yesterday* → appears
- [ ] Submit with an empty description → red "Description cannot be empty." and nothing is added
- [ ] The Amount field refuses 0 and negative numbers (widget blocks them)
- [ ] Special characters: add `O'Brien, "lunch" & snacks` as description → saves and displays correctly

## 3. Persistence (Neon database)

- [ ] Refresh the browser page → all expenses are still there
- [ ] Open Neon Console → SQL Editor → `SELECT * FROM expenses;` → rows match the app

## 4. Dashboard

- [ ] With Coffee 4.50 + Bus 2.75: metrics show Total **$7.25**, Expenses **2**, Average ≈ **$3.63**, Top category = Food — verify against your own hand math
- [ ] Donut chart "Spending by category" shows both categories with percentages
- [ ] Bar chart "Spending by month" shows the correct month bar
- [ ] Add a new expense → metrics and charts update immediately

## 5. Delete

- [ ] Click Delete on Coffee → "🗑️ Deleted …" message, row gone from table
- [ ] Refresh the page → still gone
- [ ] Delete the LAST remaining expense → the empty-state message returns

## 6. Budget

- [ ] Enter budget 100 → Save → "💰 Budget for YYYY-MM saved." message
- [ ] Progress bar appears: "$0.00 of $100.00 spent (0%)"
- [ ] Add an 85 expense → progress ≈ 85% with amber "⚠️ Close to your budget limit."
- [ ] Add a 30 expense → red "⚠️ Over budget by $15.00!"
- [ ] Switch to another month and back → the saved budget value is restored from the database
- [ ] Change the budget to 200 → Save → progress recalculates

## 7. Filters

- [ ] "Showing X of Y expenses" caption matches the visible table rows
- [ ] Deselect a category → only remaining categories are shown; metrics, table, and export all narrow
- [ ] Narrow the amount slider → out-of-range rows disappear
- [ ] Set the date range to a single day → only that day's expenses show
- [ ] Combine filters → results are the intersection (AND logic)
- [ ] Deselect ALL categories → "No expenses match the current filters." warning, no crash
- [ ] Reset filters → everything returns

## 8. CSV export

- [ ] Click "Download filtered expenses as CSV" → file `expenses_filtered.csv` downloads
- [ ] Open it → header row + exactly the rows visible in the table
- [ ] Apply a filter first → the download contains only the filtered rows

## 9. Edge cases & error handling

- [ ] Delete all data → app returns to the empty state with no errors
- [ ] Temporarily rename `.env` → app shows a friendly error (no traceback); restore the file afterwards and restart
- [ ] Very long description (100+ characters) → saves and displays
- [ ] Amount 1234.56 → displays as $1,234.56 (thousands separator)
- [ ] No red tracebacks anywhere in the app or the terminal at any point

## 10. Final pass

- [ ] Resize the browser window narrow → all sections still usable
- [ ] Restart the app (`Ctrl+C` then `streamlit run app.py`) → data and budget intact
