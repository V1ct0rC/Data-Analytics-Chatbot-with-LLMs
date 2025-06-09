import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI backend!"}

def test_create_session():
    response = client.post("/sessions", json={"name": "Test Session"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Session"
    global session_id  # Store session ID for other tests
    session_id = data["id"]

def test_get_existing_session():
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["name"] == "Test Session"

def test_get_nonexistent_session():
    response = client.get("/sessions/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"

def test_delete_session():
    # Create a new session to delete
    response = client.post("/sessions", json={"name": "Delete Me"})
    new_id = response.json()["id"]

    del_response = client.delete(f"/sessions/{new_id}")
    assert del_response.status_code == 200
    assert del_response.json()["success"] is True

# The @patch decorators you're seeing come from Python’s unittest.mock module. 
# They're used to replace ("mock") parts of your application during a test.
@patch("backend.app.main.add_csv_to_database")
def test_upload_csv(mock_add_csv):
    mock_add_csv.return_value = {"success": True}
    csv_content = b"col1,col2\nval1,val2"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    data = {"table_name": "test_table"}

    response = client.post("/upload_csv", data=data, files=files)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "created successfully" in response.json()["message"]

@patch("backend.app.main.LLMProviderFactory.get_provider")
@patch("backend.app.main.session_manager")
def test_generate_response(mock_session_manager, mock_provider_factory):
    mock_provider = mock_provider_factory.return_value
    mock_provider.generate_response.return_value = {
        "response": "This is a test response",
        "chart_data": None,
    }

    mock_session = mock_session_manager.create_session.return_value
    mock_session.id = "fake-session-id"

    mock_session_manager.get_session.return_value = mock_session
    mock_session_manager.get_messages.return_value = []

    payload = {
        "provider": "test_provider",
        "prompt": "Hello, LLM",
        "model": "default",
        "temperature": 0.7,
        "top_p": 1.0,
        "top_k": 40,
        "session_id": "fake-session-id",
    }

    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    assert response.json()["response"] == "This is a test response"

@patch("backend.app.main.LLMProviderFactory.get_provider")
@patch("backend.app.main.LLMProviderFactory.get_available_providers")
def test_get_available_providers(mock_get_available_providers, mock_get_provider):
    mock_get_available_providers.return_value = ["mock_provider"]

    # MagicMock is a flexible object from the unittest.mock module that lets you simulate 
    # (or "mock") the behavior of any Python object.
    mock_provider_instance = MagicMock()
    mock_provider_instance.get_available_models.return_value = ["model-a", "model-b"]
    mock_get_provider.return_value = mock_provider_instance

    response = client.get("/providers")

    assert response.status_code == 200
    json_data = response.json()
    assert "mock_provider" in json_data
    assert json_data["mock_provider"] == ["model-a", "model-b"]

    mock_get_available_providers.assert_called_once()
    mock_get_provider.assert_called_with("mock_provider")

@patch("backend.app.main.LLMProviderFactory.get_provider")
@patch("backend.app.main.session_manager")
@patch("backend.app.llm.agent_functions.query_database")
def test_agent_function_call_flow(mock_query_database, mock_session_manager, mock_provider_factory):
    mock_query_database.return_value = [
        {"name": "Victor", "value": 10.5},
        {"name": "Bob", "value": 20.0}
    ]

    mock_provider = mock_provider_factory.return_value
    
    def side_effect_generate_response(*args, **kwargs):
        function_result = mock_query_database("SELECT * FROM test_table")
        
        response_text = f"I found {len(function_result)} rows in the database. Victor has value 10.5 and Bob has value 20.0."
        
        return {
            "response": response_text,
            "chart_data": None,
        }
    
    mock_provider.generate_response.side_effect = side_effect_generate_response
    
    mock_session = mock_session_manager.create_session.return_value
    mock_session.id = "fake-session-id"
    mock_session_manager.get_session.return_value = mock_session
    mock_session_manager.get_messages.return_value = []
    
    payload = {
        "provider": "test_provider",
        "prompt": "What data is in the test_table?",
        "model": "default",
        "temperature": 0.7,
        "top_p": 1.0,
        "top_k": 40,
        "session_id": "fake-session-id",
    }
    
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert "I found 2 rows in the database" in response.json()["response"]
    assert "Victor has value 10.5" in response.json()["response"]
    
    mock_query_database.assert_called_once_with("SELECT * FROM test_table")