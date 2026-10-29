from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# =========================================================
# 1. PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"


# =========================================================
# 2. LOAD DATABASE CONFIGURATION
# =========================================================

load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DATABASE")


required_settings = {
    "POSTGRES_HOST": DB_HOST,
    "POSTGRES_PORT": DB_PORT,
    "POSTGRES_USER": DB_USER,
    "POSTGRES_PASSWORD": DB_PASSWORD,
    "POSTGRES_DATABASE": DB_NAME,
}

missing_settings = [
    name
    for name, value in required_settings.items()
    if not value
]

if missing_settings:
    raise ValueError(
        "Missing database settings in .env: "
        + ", ".join(missing_settings)
    )


# =========================================================
# 3. CREATE SQLALCHEMY ENGINE
# =========================================================

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(DATABASE_URL)


# =========================================================
# 4. TABLE LOAD ORDER
# =========================================================

datasets = [
    ("customers", "customers.csv"),
    (
        "product_category_name_translation",
        "product_category_name_translation.csv",
    ),
    ("orders", "orders.csv"),
    ("products", "products.csv"),
    ("sellers", "sellers.csv"),
    ("order_items", "order_items.csv"),
    ("order_payments", "order_payments.csv"),
    ("order_reviews", "order_reviews.csv"),
    ("geolocation", "geolocation.csv"),
]


# =========================================================
# 5. DATETIME COLUMNS
# =========================================================

datetime_columns = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "shipping_limit_date",
    ],
    "order_reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


# =========================================================
# 6. TEST DATABASE CONNECTION
# =========================================================

with engine.connect() as connection:
    connection.execute(text("SELECT 1"))

print("PostgreSQL connection successful!")


# =========================================================
# 7. CHECK THAT TARGET TABLES ARE EMPTY
# =========================================================

print("\nChecking target tables...")

with engine.connect() as connection:

    for table_name, _ in datasets:

        query = text(f'SELECT COUNT(*) FROM "{table_name}"')

        row_count = connection.execute(query).scalar_one()

        if row_count != 0:
            raise RuntimeError(
                f"Table '{table_name}' is not empty "
                f"({row_count:,} rows found). "
                "Stop loading to avoid duplicate records."
            )

        print(f"  {table_name}: empty")


# =========================================================
# 8. LOAD CLEANED DATA
# =========================================================

print("\nStarting data load...")

loaded_counts = {}

for table_name, file_name in datasets:

    file_path = CLEANED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {file_path}"
        )

    print(f"\nLoading {table_name}...")

    df = pd.read_csv(file_path)

    # Convert datetime columns explicitly
    if table_name in datetime_columns:

        for column in datetime_columns[table_name]:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

    # Load into the existing PostgreSQL table.
    # DO NOT use replace: schema.sql owns the table structure.
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
    )

    loaded_counts[table_name] = len(df)

    print(
        f"  Loaded {len(df):,} rows into {table_name}"
    )


# =========================================================
# 9. VALIDATE LOADED ROW COUNTS
# =========================================================

print("\nValidating loaded row counts...")

with engine.connect() as connection:

    for table_name, expected_count in loaded_counts.items():

        query = text(f'SELECT COUNT(*) FROM "{table_name}"')

        actual_count = connection.execute(query).scalar_one()

        if actual_count != expected_count:

            raise RuntimeError(
                f"Row-count mismatch for '{table_name}': "
                f"expected {expected_count:,}, "
                f"found {actual_count:,}"
            )

        print(
            f"  {table_name}: "
            f"{actual_count:,} rows OK"
        )


print("\nAll datasets loaded and validated successfully!")