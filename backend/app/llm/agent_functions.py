"""
Functions for querying a database and generating charts. Those functions are designed
to be used by an LLM agent. and work with a PostgreSQL or SQLite database.

In this module, all errors are returned to the agent as a dictionary with an "error" key.
This approach allows the agent to attempt to handle errors and provide feedback to the user.
"""
import json
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text, exc
from decimal import Decimal
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/database_queries.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

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

def query_database(sql_query: str) -> list:
    """
    Executes a SQL query string and returns the results as a list of dictionaries.

    Args:
        sql_query: The SQL query to execute against the database.

    Returns:
        A list of dictionaries representing [columns, rows] from the query result, or a dictionary with an error message if the query fails.
    """
    if not sql_query or not isinstance(sql_query, str):
        logger.warning("No SQL query provided.")
        return [{"warning": "No SQL query provided."}]
    
    logger.info(f"Executing SQL query: {sql_query}")
    
    try:
        engine = create_engine(DATABASE_URL)

        try:
            # Ensure the SQL query is safe to execute. Errors will be returned to the agent.
            with engine.connect() as conn:
                result = conn.execute(text(sql_query))

                rows = result.fetchall()
                columns = result.keys()

                result_dicts = []
                for row in rows:
                    row_dict = dict(zip(columns, row))

                    # Convert any Decimal objects to float so they can be serialized to JSON
                    for key, value in row_dict.items():
                        if isinstance(value, Decimal):
                            row_dict[key] = float(value)
                    result_dicts.append(row_dict)
                return result_dicts
               
        except exc.OperationalError as e:
            logger.error(f"Database operational query error: {e}")
            return [{"error": f"Database operational query error: {str(e)}"}]
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Database query error: {e}")
            return [{"error": f"Database query error: {str(e)}"}]
        
        except Exception as e:
            logger.error(f"Unexpected database query error: {e}")
            return [{"error": f"Unexpected database query error: {str(e)}"}]
    
    except exc.SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return [{"error": f"Database connection error: {str(e)}"}]
    
    except Exception as e:
        logger.error(f"Unexpected error during DB connection: {e}")
        return [{"error": f"Unexpected error during DB connection: {str(e)}"}]


generate_chart_declaration = {
    "name": "generate_chart",
    "description": "Generates a chart based on the provided SQL query and parameters.",
    "parameters": {
        "type": "object",
        "properties": {
            "chart_type": {
                "type": "string",
                "enum": ["bar", "line"],
                "description": "The type of chart to generate ('bar', 'line')."
            },
            "sql_query": {
                "type": "string",
                "description": "The SQL query to execute against the database."
            },
            "title": {
                "type": "string",
                "description": "The title of the chart."
            },
            "x_column": {
                "type": "string",
                "description": "The column name for the x-axis. Make sure it is a valid column in the query result."
            },
            "y_column": {
                "type": "string",
                "description": "The columns names for the y-axis. To set one column, send just the string like 'col_1'. You can set more than one column if format the list as a string like '['col_1', ...]'. Make sure that this column exists in the query result. If needed make the query forehand to ensure the columns are present."
            }
        },
        "required": ["chart_type", "sql_query", "title", "x_column", "y_column"]
    }
}

def generate_chart(chart_type: str, sql_query: str, title: str, x_column: str, y_column: str) -> dict:
    """
    Executes SQL query and returns structured data for creating charts in the frontend. Feel free to query beforehand using query_database to ensure the columns are present.

    Args:
        chart_type: The type of chart to generate ('bar', 'line').
        sql_query: The SQL query to execute against the database.
        title: The title of the chart.
        x_column: The column name for the x-axis. Make sure it is a valid column in the query result.
        y_column: The columns names for the y-axis. To set one column, send just the string like 'col_1'. You can set more than one column if format the list as a string like '["col_1", ...]'. Make sure that this column exists in the query result. If needed make the query forehand to ensure the columns are present.
    
    Returns:
        A dictionary containing the chart type, title, x_column, y_column, and data for the chart.
        If an error occurs, it returns a dictionary with success set to False and an error message.
    """
    try:
        # Get data from database using the provided SQL query. Errors will be returned to the agent.
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
        logger.error(f"Error generating chart: {e}")
        return {"success": False, "Error generating chart:": str(e)}


list_tables_declaration = {
    "name": "list_tables",
    "description": "Lists all tables in the connected database.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

def list_tables() -> list:
    """
    Lists all tables in the connected database. Works with both PostgreSQL and SQLite databases.

    Returns:
        A list of table names.
    """
    engine = create_engine(DATABASE_URL)
    try:
        # Connect to the database and retrieve the list of tables. Errors will be returned to the agent.
        with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                result = conn.execute(
                    text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                )
            elif engine.dialect.name == "sqlite":
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
            else:
                return ["Unsupported database type"]
            tables = [row[0] for row in result.fetchall()]
            return tables
    
    except exc.SQLAlchemyError as e:
        logger.error(f"Error listing tables: {e}")
        return ["Error listing tables: {str(e)}"]

    except Exception as e:
        logger.error(f"Unknown error listing tables: {e}")
        return ["Unknown error listing tables: {str(e)}"]


if __name__ == "__main__":
    sql_query = "SELECT count(sexo) FROM clientes LIMIT 5"
    results = query_database(sql_query)
    
    if results is not None:
        for row in results:
            print(row)
    else:
        print("No results found or an error occurred.")
