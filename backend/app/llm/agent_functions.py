import json
import os
import pandas as pd
from dotenv import load_dotenv

from sqlalchemy import create_engine, text, exc
from decimal import Decimal


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clientes.db")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


query_database_declaration = {
    "name": "query_database",
    "description": "Executes a SQL query string and returns the results as a list of dictionaries.",
    "parameters": {
        "type": "object",
        "properties": {
            "sql_query": {
                "type": "string",
                "description": "The SQL query to execute against the database."
            }
        },
        "required": ["sql_query"]
    }
}

def query_database(sql_query: str):
    """
    Executes a SQL query string and returns the results as a list of dictionaries.

    Args:
        sql_query: The SQL query to execute against the database.

    Returns:
        A list of dictionaries representing [columns, rows] from the query result, or None if an error occurs.
    """
    print(f"Executing SQL query: {sql_query}")

    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))

            rows = result.fetchall()
            columns = result.keys()

            print(rows)
            print(columns)
            result_dicts = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                # Convert any Decimal objects to float
                for key, value in row_dict.items():
                    if isinstance(value, Decimal):
                        row_dict[key] = float(value)
                result_dicts.append(row_dict)
            return result_dicts
        
    except exc.SQLAlchemyError as e:
        print(f"Database query error: {e}")
        return None


def generate_chart(chart_type: str, sql_query: str, title: str, x_column: str, y_column: str):
    """
    Executes SQL query and returns structured data for creating charts in the frontend.

    Args:
        chart_type: The type of chart to generate ('bar', 'line').
        sql_query: The SQL query to execute against the database.
        title: The title of the chart.
        x_column: The column name for the x-axis. Make sure it is a valid column in the query result.
        y_column: The column name for the y-axis. Make sure it is a valid column in the query result.
    """
    try:
        # Get data from database
        data = query_database(sql_query)
        if not data or len(data) == 0:
            return {"success": False, "error": "No data returned from query"}
            
        return {
            "success": True,
            "chart_type": chart_type,
            "title": title,
            "x_column": x_column,
            "y_column": y_column,
            "data": data
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Example usage
    sql_query = "SELECT * FROM clientes LIMIT 5"
    results = query_database(sql_query)
    
    if results is not None:
        for row in results:
            print(row)
    else:
        print("No results found or an error occurred.")