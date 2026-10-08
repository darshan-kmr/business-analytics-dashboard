# Business Analytics Dashboard

FastAPI + SQLite + Chart.js. One service serves both the API and the UI.

## Run
```bash
pip install -r requirements.txt
# 1. put the dataset at data/sales.xlsx   (see data/README.txt, and the comment in etl.py)
python etl.py                      # one-off: Excel -> data/sales.db (indexed)
uvicorn app:app --reload           # http://localhost:8000
```
If `data/sales.db` is missing, `app.py` runs the ETL automatically on first start.

## Architecture & decisions
- **ETL to SQLite, not reading Excel per request.** Parsing 300K rows of .xlsx takes tens of seconds, so it happens once. The app then queries a compact, indexed SQLite file (read-only connections).
- **SQLite over Postgres:** the data is read-only and fits comfortably on one machine; zero infrastructure to deploy. Trade-off: it would not scale to concurrent writes or much larger data.
- **Aggregation in SQL.** The browser never receives raw rows - only a few KB of aggregates, so the page stays fast.
- **Derived at load time:** `revenue = Price x Quantity`, `d` (ISO date) and `hour`. Indexes on date and every filter column.
- **Caching:** results are memoised per filter combination (`lru_cache`) and the unfiltered view is pre-warmed at startup. Safe because the data is static after ETL.
- **Trend grain:** daily, auto-rolled up to monthly when the range exceeds 120 days.
- **Bonus:** CSV export of the filtered data, responsive layout, dark mode, gzip.

## Assumptions
- `BillNo` is only assumed unique per outlet, so an order = `(Outlet_Name, BillNo)`. Orders = distinct such pairs; AOV = revenue / orders.
- Rows with an unparseable `Order_Datetime` are dropped. Currency is shown as INR.
- Filters are single-select and combine with AND.

## Deployment
Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`. Either commit `data/sales.xlsx` and let the app build the DB on first boot, or build locally and commit `data/sales.db` (remove it from `.gitignore`) for faster cold starts.

**Live URL:** _add here_
