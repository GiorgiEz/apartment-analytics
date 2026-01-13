from config import paths
from sqlalchemy import create_engine, text
import pandas as pd
import os


class PostgresDatabase:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        self.engine = create_engine(db_url)

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

    def _fetch_one(self, query):
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.scalar()

    def get_all_apartments(self):
        """ Calls dw.all_apartments VIEW to get all apartments data from postgresql database """
        query = """SELECT * FROM dw.all_apartments_view"""
        return pd.read_sql(query, self.engine, parse_dates=["upload_date"])

    def write_all_apartments_data_to_csv(self, path):
        self.get_all_apartments().to_csv(path, index=False)

    def database_insertion(self, writ_from_path=paths.APARTMENTS_PROCESSED_PATH):
        # 1. Load to staging
        df = pd.read_csv(writ_from_path)
        self.__load_to_staging(df)

        # 2. Run DML
        self.__run_sql_file(paths.DML_ETL_FROM_STAGING_04_PATH)

        # 3. Fetch fact table row count
        fact_count = self._fetch_one("SELECT COUNT(*) FROM dw.fct_apartments")
        print(f"PostgreSQL | fct_apartments rows: {fact_count}")
