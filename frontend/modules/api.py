import requests
import uuid

def load_sessions(backend_url):
    """Load all sessions from the backend."""
    try:
        response = requests.get(f"{backend_url}/sessions")
        if response.status_code == 200:
            return response.json(), True
        return [], False
    except Exception as e:
        return [], f"Error loading sessions: {str(e)}"

def load_messages(backend_url, session_id):
    """Load messages for a specific session."""
    try:
        response = requests.get(f"{backend_url}/sessions/{session_id}/messages")
        if response.status_code == 200:
            return response.json(), True
        return [], False
    except Exception as e:
        return [], f"Error loading messages: {str(e)}"

def create_session(backend_url, name):
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

def send_message(backend_url, prompt, session_id):
    """Send a message to the backend and get a response."""
    try:
        response = requests.post(
            f"{backend_url}/gemini",
            json={
                "prompt": prompt,
                "session_id": session_id
            }
        )
        if response.status_code == 200:
            return response.json(), True
        return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error connecting to backend: {str(e)}"