import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import etl

DB=etl.DB
if not os.path.exists(DB):
    etl.run()

app=FastAPI(
    title="Business Analytics Dashboard"
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

def get_db():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    return conn

def build_filters(
    start_date: Optional[str]=None,
    end_date: Optional[str]=None,
    brand: Optional[str]=None,
    outlet: Optional[str]=None,
    category: Optional[str]=None,
    order_type: Optional[str]=None,
    settlement: Optional[str]=None
):
    conditions=[]
    params=[]

    if start_date:
        conditions.append("order_date >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("order_date <= ?")
        params.append(end_date)

    if brand and brand != "All":
        conditions.append("brand = ?")
        params.append(brand)

    if outlet and outlet != "All":
        conditions.append("outlet_name = ?")
        params.append(outlet)

    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)

    if order_type and order_type != "All":
        conditions.append("order_type = ?")
        params.append(order_type)

    if settlement and settlement != "All":
        conditions.append("settlement = ?")
        params.append(settlement)

    where=""

    if conditions:
        where="WHERE " + " AND ".join(conditions)

    return where, params

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api/filters")
def filters():
    conn=get_db()
    result={}
    columns={
        "brands": "brand",
        "outlets": "outlet_name",
        "categories": "category",
        "order_types": "order_type",
        "settlements": "settlement"
    }
    for key, column in columns.items():
        rows=conn.execute(
            f"""
            SELECT DISTINCT {column}
            FROM orders
            WHERE {column} IS NOT NULL
              AND {column} != ''
            ORDER BY {column}
            """
        ).fetchall()

        result[key]=[
            row[0] for row in rows
        ]

    dates=conn.execute(
        """
        SELECT
            MIN(order_date),
            MAX(order_date)
        FROM orders
        """
    ).fetchone()

    result["min_date"]=dates[0]
    result["max_date"]=dates[1]

    conn.close()

    return result

@app.get("/api/summary")
def summary(
    start_date: Optional[str]=None,
    end_date: Optional[str]=None,
    brand: Optional[str]=None,
    outlet: Optional[str]=None,
    category: Optional[str]=None,
    order_type: Optional[str]=None,
    settlement: Optional[str]=None
):
    where, params=build_filters(
        start_date,
        end_date,
        brand,
        outlet,
        category,
        order_type,
        settlement
    )

    conn=get_db()

    query=f"""
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT billno) AS total_orders,
            COALESCE(SUM(revenue), 0) AS total_revenue,
            COALESCE(SUM(quantity), 0) AS total_items
        FROM orders
        {where}
    """

    row=conn.execute(
        query,
        params
    ).fetchone()

    total_revenue=row["total_revenue"]
    total_orders=row["total_orders"]

    average_order_value=(
        total_revenue / total_orders
        if total_orders
        else 0
    )

    return {
        "total_records": row["total_records"],
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_items": row["total_items"],
        "average_order_value": average_order_value
    }

@app.get("/api/revenue-trend")
def revenue_trend(
    start_date: Optional[str]=None,
    end_date: Optional[str]=None,
    brand: Optional[str]=None,
    outlet: Optional[str]=None,
    category: Optional[str]=None,
    order_type: Optional[str]=None,
    settlement: Optional[str]=None
):
    where, params=build_filters(
        start_date,
        end_date,
        brand,
        outlet,
        category,
        order_type,
        settlement
    )

    conn=get_db()

    rows=conn.execute(
        f"""
        SELECT
            order_date AS date,
            SUM(revenue) AS revenue
        FROM orders
        {where}
        GROUP BY order_date
        ORDER BY order_date
        """,
        params
    ).fetchall()

    conn.close()

    return [
        {
            "date": row["date"],
            "revenue": row["revenue"]
        }
        for row in rows
    ]

@app.get("/api/revenue-by-category")
def revenue_by_category(
    start_date: Optional[str]=None,
    end_date: Optional[str]=None,
    brand: Optional[str]=None,
    outlet: Optional[str]=None,
    category: Optional[str]=None,
    order_type: Optional[str]=None,
    settlement: Optional[str]=None
):
    where, params=build_filters(
        start_date,
        end_date,
        brand,
        outlet,
        category,
        order_type,
        settlement
    )

    conn=get_db()

    rows=conn.execute(
        f"""
        SELECT
            category,
            SUM(revenue) AS revenue
        FROM orders
        {where}
        GROUP BY category
        ORDER BY revenue DESC
        """,
        params
    ).fetchall()

    conn.close()

    return [
        {
            "category": row["category"],
            "revenue": row["revenue"]
        }
        for row in rows
    ]

@app.get("/api/order-types")
def order_types(
    start_date: Optional[str]=None,
    end_date: Optional[str]=None,
    brand: Optional[str]=None,
    outlet: Optional[str]=None,
    category: Optional[str]=None,
    order_type: Optional[str]=None,
    settlement: Optional[str]=None
):
    where, params=build_filters(
        start_date,
        end_date,
        brand,
        outlet,
        category,
        order_type,
        settlement
    )

    conn=get_db()

    rows=conn.execute(
        f"""
        SELECT
            order_type,
            COUNT(DISTINCT billno) AS orders
        FROM orders
        {where}
        GROUP BY order_type
        ORDER BY orders DESC
        """,
        params
    ).fetchall()

    conn.close()

    return [
        {
            "order_type": row["order_type"],
            "orders": row["orders"]
        }
        for row in rows
    ]

@app.get("/api/top-items")
def top_items(
    start_date: Optional[str]=None,
    end_date: Optional[str]=None,
    brand: Optional[str]=None,
    outlet: Optional[str]=None,
    category: Optional[str]=None,
    order_type: Optional[str]=None,
    settlement: Optional[str]=None
):
    where, params=build_filters(
        start_date,
        end_date,
        brand,
        outlet,
        category,
        order_type,
        settlement
    )

    conn=get_db()

    rows=conn.execute(
        f"""
        SELECT
            item,
            SUM(quantity) AS quantity,
            SUM(revenue) AS revenue
        FROM orders
        {where}
        GROUP BY item
        ORDER BY revenue DESC
        LIMIT 10
        """,
        params
    ).fetchall()

    conn.close()

    return [
        {
            "item": row["item"],
            "quantity": row["quantity"],
            "revenue": row["revenue"]
        }
        for row in rows
    ]

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)