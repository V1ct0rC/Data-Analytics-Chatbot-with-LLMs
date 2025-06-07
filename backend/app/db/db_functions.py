import pandas as pd
import os
from sqlalchemy import create_engine
from io import StringIO


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL)

def add_csv_to_database(table_name, file_bytes):
    """
    Add a CSV file as a new table in the database.
    Args:
        table_name (str): Name of the table to create.
        file_bytes (bytes): CSV file content.
    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        try:
            df = pd.read_csv(StringIO(file_bytes.decode("utf-8")))
        except UnicodeDecodeError:
            df = pd.read_csv(StringIO(file_bytes.decode("latin1")))

        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=200
        )
        print(f"Added {len(df)} records to {table_name}")
        return {"success": True, "message": f"Table '{table_name}' created successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    