import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "hotel_bookings.csv"
SCHEMA = "raw"
TABLE = "bookings"


def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def main():
    print(f"Reading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False, na_values=[""])
    print(f"Rows in CSV: {len(df):,}  Columns: {len(df.columns)}")

    engine = get_engine()

    df.to_sql(
        TABLE,
        engine,
        schema=SCHEMA,
        if_exists="append",
        index=False,
        chunksize=10_000,
        method="multi",
    )

    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")).scalar()
    print(f"Rows in {SCHEMA}.{TABLE}: {count:,}")


if __name__ == "__main__":
    main()