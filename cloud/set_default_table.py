"""
This script prepares default data for the database and creates necessary tables. This data 
is loaded from a CSV file hosted on GitHub, as requested for the challenge.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/database_operations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

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
    df["classe_social"] = df["classe_social"].str.strip().str.upper()
    df["sexo"] = df["sexo"].str.strip().str.upper()

    return df[cols]


def start_database():
    """
    Start the database by creating necessary tables and loading default data.
    """
    
    try:
        df = prepare_default_data()
    except Exception as e:
        logger.error(f"Failed to prepare data: {e}")
        logger.info("Exiting without starting the database.")
        return

    try:
        engine = create_engine(DATABASE_URL)

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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            # Create chat_messages table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            logger.info(f"Successfully loaded {len(df)} records into the 'clientes' table.")

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during database operations: {e}")
        logger.info("Exiting without starting the database.")
        return
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.info("Exiting without starting the database.")
        return
    
    finally:
        if engine:
            engine.dispose(close=True)


if __name__ == "__main__":
    try:
        logger.info(f"Using database URL: {DATABASE_URL}")
        start_database()

        # Just a test to see if the database is working with the default dataset
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM clientes"))
            count = result.scalar()
            logger.info(f"Total records in the database: {count}")

    except Exception as e:
        logger.error(f"Unknown error during database initialization: {e}", exc_info=True)
