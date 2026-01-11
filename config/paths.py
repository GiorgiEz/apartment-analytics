# config/paths.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ======================
# Data (CSV lifecycle)
# ======================
DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Raw CSVs (per source)
LIVO_APARTMENTS_RAW_PATH = RAW_DATA_DIR / "livo_apartments.csv"
MYHOME_APARTMENTS_RAW_PATH = RAW_DATA_DIR / "myhome_apartments.csv"
SSHOME_APARTMENTS_RAW_PATH = RAW_DATA_DIR / "sshome_apartments.csv"

# Canonical cleaned CSV
APARTMENTS_PROCESSED_PATH = PROCESSED_DATA_DIR / "apartments.csv"

# ======================
# Data storage (serving layer)
# ======================
DATASTORAGE_DIR = PROJECT_ROOT / "datastorage"

CSV_STORAGE_DIR = DATASTORAGE_DIR / "csv"
SQLITE_DIR = DATASTORAGE_DIR / "sqlite"
POSTGRESQL_DIR = DATASTORAGE_DIR / "postgresql"

STREET_TO_DISTRICT_JSON_PATH = DATASTORAGE_DIR / "extra_data" / "street_to_district.json"
TBILISI_CANONICAL_DISTRICTS_PATH = DATASTORAGE_DIR / "extra_data" / "tbilisi_canonical_districts.json"

# Stored CSV (historical / merged)
APARTMENTS_CSV_PATH = CSV_STORAGE_DIR / "apartments.csv"

# Databases
APARTMENTS_SQLITE_DB_PATH = SQLITE_DIR / "apartments.db"

# Storage backups
SQLITE_DB_BACKUPS_DIR = SQLITE_DIR / "sqlite_backups"

# POSTGRESQL scripts directory
POSTGRESQL_SCRIPTS_DIR = POSTGRESQL_DIR / "sql"

#POSGRESQL script files
DML_ETL_FROM_STAGING_04_PATH = POSTGRESQL_SCRIPTS_DIR / "04_DML_ETL_FROM_STAGING.sql"
