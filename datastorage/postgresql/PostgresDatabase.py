from config import paths
from sqlalchemy import create_engine, text
import pandas as pd
import os
from pathlib import Path


class PostgresDatabase:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        self.engine = create_engine(db_url)
        self.write_from_csv = paths.APARTMENTS_PROCESSED_PATH

    def __load_to_staging(self, df):
        """ Append processed data into sa.apartments """
        df.to_sql(
            name="apartments",
            con=self.engine,
            schema="sa",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000
        )

    def __run_sql_file(self, path):
        """ Execute a SQL script (DDL/DML/etc) """
        with self.engine.begin() as conn:
            with open(path, "r", encoding="utf-8") as f:
                conn.execute(text(f.read()))

    def __fetch_one(self, query):
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.scalar()

    def database_insertion(self):
        # 1. Load to staging
        df = pd.read_csv(self.write_from_csv)
        self.__load_to_staging(df)

        # 2. Run DML
        self.__run_sql_file(paths.DML_ETL_FROM_STAGING_04_PATH)

        # 3. Fetch fact table row count
        fact_count = self.__fetch_one("SELECT COUNT(*) FROM dw.fct_apartments")
        print(f"PostgreSQL | fct_apartments rows: {fact_count}")
