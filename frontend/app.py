from ast import literal_eval
import streamlit as st
import requests
import uuid
import os
import pandas as pd

from modules.api import load_sessions, load_messages, create_session, send_message


st.set_page_config(page_title="Data Analysis Chatbot", layout="wide")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


def load_sessions_from_backend():
    """Load all sessions and their messages from the backend."""
    try:
        # Get all sessions
        response = requests.get(f"{BACKEND_URL}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            
            for session in sessions:
                session_id = session["id"]
                
                if session_id in st.session_state.chat_sessions:
                    continue
                    
                msg_response = requests.get(f"{BACKEND_URL}/sessions/{session_id}/messages")
                if msg_response.status_code == 200:
                    messages = msg_response.json()
                    
                    # Convert to the format used in frontend
                    frontend_messages = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in messages
                    ]
                    
                    st.session_state.chat_sessions[session_id] = frontend_messages
                    st.session_state.session_names[session_id] = session.get("name", f"Chat {session_id[:6]}")
                    
                    if session_id not in st.session_state.chart_history:
                        st.session_state.chart_history[session_id] = []
            
            if st.session_state.current_chat_id is None and st.session_state.chat_sessions:
                st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
                
            return True
        return False
    except Exception as e:
        st.error(f"Error loading sessions: {str(e)}")
        return False

def initialize_session_state():
    """Initialize session state variables."""

    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
        st.session_state.session_names = {}

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    if "show_landing_page" not in st.session_state:
        st.session_state.show_landing_page = True

    if "current_chart_data" not in st.session_state:
        st.session_state.current_chart_data = None

    if "chart_history" not in st.session_state:
        st.session_state.chart_history = {}

    # Load existing sessions from backend
    if "sessions_loaded" not in st.session_state:
        sessions_loaded = load_sessions_from_backend()
        st.session_state.sessions_loaded = True
        
        # If sessions were loaded and this is first run, skip landing page
        if sessions_loaded and st.session_state.chat_sessions:
            st.session_state.show_landing_page = False

def start_chatting():
    """Callback to hide the landing page and show the chat interface."""

    st.session_state.show_landing_page = False

def render_landing_page():
    """Render the landing page with a welcome message and instructions."""

    col1, col2 = st.columns([1, 2])
    with col1:
        st.title("Welcome to the Data Analysis Chatbot")
        st.markdown("""
        ### Your AI Assistant for Data Analysis
        
        This chatbot helps you analyze and understand your data through natural conversations.
        
        **Features:**
        - Ask questions about your data in plain English
        - Get visualizations and insights automatically
        - Multiple chat sessions to organize your work
        - Save and export your analysis results
        
        **Example questions you can ask:**
        - "What are the trends in my sales data over the last quarter?"
        - "Create a visualization showing the relationship between X and Y"
        - "Summarize the key insights from this dataset"
        """)
        
        st.button("Start Chatting", on_click=start_chatting, type="primary", use_container_width=True)
    
    with col2:
        st.image("frontend/assets/landing_page_art_2_small.png", use_container_width=True)

def render_sidebar():
    """Render the sidebar for chat session management."""

    with st.sidebar:
        st.title("Chat Sessions")
        
        # Create new chat session --------------------------------------------------------------------------
        if st.button("New Chat", use_container_width=True):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/sessions",
                    json={"name": f"Chat ({uuid.uuid4().hex[:6]})"}
                )

                if response.status_code == 200:
                    session_data = response.json()
                    backend_session_id = session_data["id"]
                    session_name = session_data["name"]
                    
                    st.session_state.chat_sessions[backend_session_id] = []
                    st.session_state.current_chat_id = backend_session_id
                    
                    st.session_state.session_names[backend_session_id] = session_name
                else:
                    st.error(f"Failed to create session: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")
        
        # Display chat sessions ----------------------------------------------------------------------------
        if st.session_state.chat_sessions:
            st.write("Your chats:")

            with st.container(height=300):
                for chat_id in st.session_state.chat_sessions.keys():
                    col1, col2 = st.columns([4, 1])
                    
                    display_name = st.session_state.session_names.get(chat_id, chat_id) if hasattr(st.session_state, "session_names") else chat_id
                    
                    if chat_id == st.session_state.current_chat_id:
                        button_label = f":small_blue_diamond: {display_name}"
                    else:
                        button_label = display_name
                        
                    if col1.button(button_label, key=f"select_{chat_id}", use_container_width=True):
                        st.session_state.current_chat_id = chat_id
                        
                        if chat_id in st.session_state.chart_history and st.session_state.chart_history[chat_id]:
                            st.session_state.current_chart_data = st.session_state.chart_history[chat_id][-1]
                        else:
                            st.session_state.current_chart_data = None
                            
                        st.rerun()
                    
                    if len(st.session_state.chat_sessions) > 1:
                        if col2.button(":x:", key=f"delete_{chat_id}"):
                            try:
                                response = requests.delete(f"{BACKEND_URL}/sessions/{chat_id}")
                                if response.status_code == 200:
                                    del st.session_state.chat_sessions[chat_id]
                                    if hasattr(st.session_state, "session_names"):
                                        del st.session_state.session_names[chat_id]
                                    if chat_id in st.session_state.chart_history:
                                        del st.session_state.chart_history[chat_id]
                                    if chat_id == st.session_state.current_chat_id:
                                        st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete session: {response.text}")
                            except Exception as e:
                                st.error(f"Error deleting session: {str(e)}")

        st.markdown("#### Add a new table (CSV)", help="We do not perform any data validation or transformation. Please ensure your CSV is clean and ready for analysis.")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="csv_uploader")
        table_name = st.text_input("Table name", key="table_name_input")
        if uploaded_file and table_name:
            if st.button("Upload and Create Table", key="upload_csv_btn"):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    data = {"table_name": table_name}
                    response = requests.post(
                        f"{BACKEND_URL}/upload_csv",
                        files=files,
                        data=data
                    )
                    result = response.json()
                    if result.get("success"):
                        st.success(result.get("message"))
                    else:
                        st.error(result.get("message"))
                except Exception as e:
                    st.error(f"Upload failed: {e}")

def parse_y_column(y_column):
    """Parse the y_column input to handle both string and list formats."""
    try:
        return literal_eval(y_column)
    except Exception:
        return y_column

def render_chat_area():
    """Render the main chat area where users can interact with the chatbot."""

    st.title("Data Analysis Chatbot")

    if st.session_state.current_chat_id is None or not st.session_state.chat_sessions:
        st.info("👈 Click the 'New Chat' button in the sidebar to start a conversation.")

    else:
        chat_col, viz_col = st.columns([2, 1])

        with chat_col:
            # Get and display current chat messages ----------------------------------------------------------------
            current_messages = st.session_state.chat_sessions[st.session_state.current_chat_id]

            chat_container = st.container(height=450)
            with chat_container:
                for message in current_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Input field for user messages ------------------------------------------------------------------------
            input_container = st.container()
            with input_container:
                with st.expander("Advanced LLM Settings"):
                    col1, col2 = st.columns(2)
                    temperature = st.slider(
                        "Temperature", 
                        min_value=0.0, 
                        max_value=2.0, 
                        value=0.2, 
                        step=0.05,
                        help="Higher values make output more random, lower values more deterministic"
                    )
                    with col1:
                        top_p = st.slider(
                            "Top P", 
                            min_value=0.0, 
                            max_value=1.0, 
                            value=0.95, 
                            step=0.05,
                            help="Controls diversity via nucleus sampling"
                        )
                    with col2:
                        top_k = st.slider(
                            "Top K", 
                            min_value=1, 
                            max_value=100, 
                            value=30, 
                            step=1,
                            help="Controls diversity by limiting to top K tokens"
                        )
                
                if "submit_pressed" not in st.session_state:
                    st.session_state.submit_pressed = False
                
                with st.form(key="message_form", clear_on_submit=True):
                    user_input = st.text_input("Ask a question about your data:", key="user_input")
                    submit_button = st.form_submit_button("Send")
                    
                    if submit_button and user_input:
                        # Add user message to chat history
                        current_messages.append({"role": "user", "content": user_input})
                        
                        with chat_container:
                            # Show user message
                            with st.chat_message("user"):
                                st.markdown(user_input)
                            
                            # Show assistant response
                            with st.chat_message("assistant"):
                                with st.spinner("Thinking..."):
                                    try:
                                        backend_session_id = st.session_state.current_chat_id

                                        response = requests.post(
                                            f"{BACKEND_URL}/gemini",
                                            json={
                                                "prompt": user_input,
                                                "temperature": temperature,
                                                "top_p": top_p,
                                                "top_k": top_k,
                                                "session_id": backend_session_id
                                            }
                                        )
                                        
                                        if response.status_code == 200:
                                            result = response.json()
                                            answer = result["response"]
                                            
                                            if not backend_session_id:
                                                st.session_state[f"backend_session_{st.session_state.current_chat_id}"] = result["session_id"]
                                            
                                            if "chart_data" in result and result["chart_data"] and result["chart_data"]["success"]:
                                                session_id = st.session_state.current_chat_id
                                                
                                                if session_id not in st.session_state.chart_history:
                                                    st.session_state.chart_history[session_id] = []
                                                
                                                st.session_state.chart_history[session_id].append(result["chart_data"])
                                                
                                                st.session_state.current_chart_data = result["chart_data"]
                                        else:
                                            answer = f"Error: {response.status_code} - {response.text}"
                                    except Exception as e:
                                        answer = f"Error connecting to backend: {str(e)}"
                                    
                                    st.markdown(answer)
                        
                        current_messages.append({"role": "assistant", "content": answer})
                        st.rerun()
        
        with viz_col:
            st.text("Visualizations")
            viz_container = st.container(height=645)
            with viz_container:
                current_session_id = st.session_state.current_chat_id
                session_charts = st.session_state.chart_history.get(current_session_id, [])
                
                if not session_charts:
                    st.info("No visualizations yet. Ask for a chart to see visualizations here.")
                else:
                    for i, chart_data in enumerate(session_charts):
                        if chart_data["success"]:
                            with st.container():
                                st.markdown(f"#### {chart_data['title']}")
                                
                                df = pd.DataFrame(chart_data["data"])
                                
                                tab1, tab2 = st.tabs(["Chart", "Dataframe"])

                                if chart_data["chart_type"] == "bar":
                                    tab1.bar_chart(df, x=chart_data["x_column"], y=parse_y_column(chart_data["y_column"]))
                                        
                                elif chart_data["chart_type"] == "line":
                                    tab1.line_chart(df, x=chart_data["x_column"], y=parse_y_column(chart_data["y_column"]))
                                    
                                elif chart_data["chart_type"] == "scatter":
                                    tab1.scatter_chart(df, x=chart_data["x_column"], y=parse_y_column(chart_data["y_column"]))

                                tab2.dataframe(df, use_container_width=True)
                            
                                if i < len(session_charts) - 1:
                                    st.divider()
                                
                                st.download_button(
                                    f"Download data",
                                    df.to_csv(index=False).encode('utf-8'),
                                    f"{chart_data['title'].lower().replace(' ', '_')}.csv",
                                    "text/csv",
                                    key=f"download_{i}"
                                )


# Main execution -------------------------------------------------------------------------------------------
initialize_session_state()

# Display landing page -------------------------------------------------------------------------------------
if st.session_state.show_landing_page:
    render_landing_page()
    
else:
    # Sidebar for chat session management ------------------------------------------------------------------
    render_sidebar()

    # Main chat area ---------------------------------------------------------------------------------------
    render_chat_area()
