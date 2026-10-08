import os
import sqlite3
import pandas as pd

DB="analytics.db"
EXCEL_FILE="data/data.xlsx"

def run():
    print("Reading Excel file...")
    df=pd.read_excel(EXCEL_FILE)
    print(f"Loaded {len(df):,} rows")
    df.columns=[str(col).strip().lower().replace(" ", "_") for col in df.columns]
    print("Columns:", list(df.columns))
    if "group" in df.columns:
        df.rename(columns={"group": "category"}, inplace=True)
    df["order_datetime"]=pd.to_datetime(df["order_datetime"], format="%d-%m-%Y %H:%M:%S", errors="coerce")
    df["price"]=pd.to_numeric(df["price"], errors="coerce")
    df["quantity"]=pd.to_numeric(df["quantity"], errors="coerce")
    df=df.dropna(subset=["billno", "order_datetime", "price", "quantity"])
    df["revenue"]=df["price"] * df["quantity"]
    df["order_date"]=df["order_datetime"].dt.strftime("%Y-%m-%d")
    df["order_datetime"]=df["order_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    text_columns=["billno", "outlet_name", "category", "order_type", "item", "settlement", "brand"]
    for col in text_columns:
        if col in df.columns:
            df[col]=df[col].fillna("").astype(str).str.strip()
    print("Creating SQLite database...")
    if os.path.exists(DB):
        os.remove(DB)
    conn=sqlite3.connect(DB)
    df.to_sql("orders", conn, if_exists="replace", index=False, chunksize=10000)
    print("Creating indexes...")
    indexes=[
        "CREATE INDEX idx_billno ON orders(billno)",
        "CREATE INDEX idx_order_date ON orders(order_date)",
        "CREATE INDEX idx_brand ON orders(brand)",
        "CREATE INDEX idx_outlet ON orders(outlet_name)",
        "CREATE INDEX idx_category ON orders(category)",
        "CREATE INDEX idx_order_type ON orders(order_type)",
        "CREATE INDEX idx_settlement ON orders(settlement)"
    ]
    for index in indexes:
        conn.execute(index)
    conn.commit()
    count=conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    orders=conn.execute("SELECT COUNT(DISTINCT billno) FROM orders").fetchone()[0]
    revenue=conn.execute("SELECT SUM(revenue) FROM orders").fetchone()[0]
    conn.close()
    print()
    print("=" * 50)
    print("ETL COMPLETE")
    print("=" * 50)
    print(f"Records : {count:,}")
    print(f"Orders  : {orders:,}")
    print(f"Revenue : {revenue:,.2f}")
    print("=" * 50)

if __name__=="__main__":
    run()