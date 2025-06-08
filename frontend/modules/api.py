import requests
import uuid
from typing import Dict, Tuple, List, Any, Optional

def load_sessions(backend_url: str) -> Tuple[List[Dict], bool]:
    """Load all sessions from the backend."""
    try:
        response = requests.get(f"{backend_url}/sessions")
        if response.status_code == 200:
            return response.json(), True
        return [], False
    except Exception as e:
        return [], f"Error loading sessions: {str(e)}"

def load_messages(backend_url: str, session_id: str) -> Tuple[List[Dict], bool]:
    """Load messages for a specific session."""
    try:
        response = requests.get(f"{backend_url}/sessions/{session_id}/messages")
        if response.status_code == 200:
            return response.json(), True
        return [], False
    except Exception as e:
        return [], f"Error loading messages: {str(e)}"

def create_session(backend_url: str, name: str) -> Tuple[Dict, bool]:
    """Create a new chat session."""
    try:
        response = requests.post(
            f"{backend_url}/sessions",
            json={"name": name}
        )
        if response.status_code == 200:
            return response.json(), True
        return None, f"Failed to create session: {response.text}"
    except Exception as e:
        return None, f"Error connecting to backend: {str(e)}"

def send_message(
    backend_url: str, prompt: str, session_id: str, provider: str = "gemini", model: Optional[str] = None,
    temperature: float = 0.2, top_p: float = 0.95, top_k: int = 30
) -> Tuple[Dict, Any]:
    """Send a message to the backend and get a response using the specified provider."""
    try:
        response = requests.post(
            f"{backend_url}/generate",
            json={
                "prompt": prompt,
                "provider": provider,
                "model": model,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "session_id": session_id
            }
        )
        if response.status_code == 200:
            return response.json(), True
        return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error connecting to backend: {str(e)}"

def upload_csv(backend_url: str, file_content, file_name: str, table_name: str) -> Tuple[Dict, bool]:
    """Upload a CSV file to the backend."""
    try:
        files = {"file": (file_name, file_content)}
        data = {"table_name": table_name}
        response = requests.post(
            f"{backend_url}/upload_csv",
            files=files,
            data=data
        )
        if response.status_code == 200:
            return response.json(), True
        return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error uploading CSV: {str(e)}"

def get_available_providers(backend_url: str) -> Tuple[Dict, bool]:
    """Get available LLM providers and their models from the backend."""
    try:
        response = requests.get(f"{backend_url}/providers")
        if response.status_code == 200:
            return response.json(), True
        return {}, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return {}, f"Error getting providers: {str(e)}"