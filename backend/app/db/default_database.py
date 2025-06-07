"""
This script prepares default data for the database and creates necessary tables. This data 
is loaded from a CSV file hosted on GitHub, as requested for the challenge.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL)

def prepare_default_data():
    """
    Prepare default data for the database. This function loads data from a CSV filea and 
    processes it.

    Returns:
        pd.DataFrame: Processed DataFrame with desired columns.
    """
    column_mapping = {
        "REF_DATE": "ref_date",
        "TARGET": "target",
        "VAR2": "sexo",
        "IDADE": "idade",
        "VAR4": "flag_obito",
        "VAR5": "uf",
        "VAR8": "classe_social"
    }

    cols = ["ref_date", "target", "sexo", "idade", "flag_obito", "uf", "classe_social"]
    df = pd.read_csv(
        "https://github.com/Neurolake/challenge-data-scientist/raw/refs/heads/main/datasets/credit_01/train.gz",
        usecols=list(column_mapping.keys()),
        parse_dates=["REF_DATE"],
        dtype={
            "target": "int8",
            "idade": "int8",
            "flag_obito": "str",
            "uf": "str",
            "classe_social": "str",
            "sexo": "str"
        },
        encoding='utf-8',
    )

    df = df.rename(columns=column_mapping)

    df["uf"] = df["uf"].str.strip().str.upper()
    df["classe_social"] = df["classe_social"].str.strip()
    df["sexo"] = df["sexo"].str.strip().str.upper()

    return df[cols]


def start_database():
    """
    Start the database by creating necessary tables and loading default data.
    """

    df = prepare_default_data()

    try:
        with engine.connect() as conn:
            # Create default clientes table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS clientes (
                    ref_date DATE,
                    target INTEGER,
                    sexo CHAR(1),
                    idade INTEGER,
                    flag_obito CHAR(1),
                    uf CHAR(2),
                    classe_social CHAR(1)
                );
            """))
            # Create chat_sessions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """))
            # Create chat_messages table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
                );
            """))
            conn.commit()
            
            df.to_sql(
                name="clientes",
                con=conn,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=200
            )
            print(f"Successfully loaded {len(df)} records into the 'clientes' table.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        start_database()

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM clientes"))
            count = result.scalar()
            print(f"Total records in the database: {count}")

            result = conn.execute(text("SELECT * FROM clientes LIMIT 5"))
            for row in result:
                print(row)

            #list all tables in the database
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            print("Tables in the database:")
            for table in tables:
                print(table[0])
    except Exception as e:
        print(f"An error occurred while counting records: {e}")
