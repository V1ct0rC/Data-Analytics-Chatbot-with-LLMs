import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from sqlalchemy import create_engine, text
from backend.app.llm.agent_functions import query_database, generate_chart, list_tables

# Setup a temporary SQLite database for testing
TEST_DB_URL = "sqlite:///test_agent_functions.db"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Create a test table and insert some data
    engine = create_engine(TEST_DB_URL)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS test_table"))
        conn.execute(text("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        """))
        conn.execute(text("INSERT INTO test_table (name, value) VALUES ('Victor', 10.5), ('Bob', 20.0)"))
        conn.commit()
    import backend.app.llm.agent_functions as agent_functions
    agent_functions.DATABASE_URL = TEST_DB_URL
    yield
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS test_table"))
        conn.commit()

def test_query_database_valid():
    sql = "SELECT * FROM test_table"
    result = query_database(sql)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Victor"
    assert result[1]["value"] == 20.0

def test_query_database_invalid_sql():
    sql = "SELECT * FROM non_existing_table"
    result = query_database(sql)
    assert isinstance(result, list)
    assert "error" in result[0]

def test_query_database_no_sql():
    result = query_database("")
    assert isinstance(result, list)
    assert "error" in result[0]

def test_generate_chart_success():
    sql = "SELECT name, value FROM test_table"
    chart = generate_chart(
        chart_type="bar",
        sql_query=sql,
        title="Test Chart",
        x_column="name",
        y_column="value"
    )
    assert chart["success"] is True
    assert chart["chart_type"] == "bar"
    assert chart["title"] == "Test Chart"
    assert isinstance(chart["data"], list)
    assert chart["x_column"] == "name"
    assert chart["y_column"] == "value"

def test_generate_chart_no_data():
    sql = "SELECT * FROM test_table WHERE id = -1"
    chart = generate_chart(
        chart_type="bar",
        sql_query=sql,
        title="Empty Chart",
        x_column="name",
        y_column="value"
    )
    assert chart["success"] is False
    assert "No data returned" in chart["error"]

def test_list_tables():
    tables = list_tables()
    assert isinstance(tables, list)
    assert "test_table" in tables
