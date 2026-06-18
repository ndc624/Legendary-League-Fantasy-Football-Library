import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "legendary_league.db"

CSV_TABLES = {
    DATA_DIR / "matchups_master.csv": "matchups",
    DATA_DIR / "all_rosters_master.csv": "rosters",
    DATA_DIR / "standings_master.csv": "standings",
    DATA_DIR / "champions.csv": "champions",
}

def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def load_csvs_to_sqlite():
    conn = sqlite3.connect(DB_PATH)

    for csv_path, table_name in CSV_TABLES.items():
        df = pd.read_csv(csv_path)
        df = clean_columns(df)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        print(f"Loaded {csv_path} into {table_name}")

    conn.close()

if __name__ == "__main__":
    load_csvs_to_sqlite()