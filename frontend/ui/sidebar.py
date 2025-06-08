import streamlit as st
import uuid
import requests
from modules.api import create_session, upload_csv, get_available_providers

def render_sidebar(backend_url: str) -> None:
    """Render the sidebar for chat session management and data upload."""
    with st.sidebar:
        st.title("Chat Sessions")
        
        # Create new chat session
        if st.button("New Chat", use_container_width=True):
            try:
                session_data, success = create_session(
                    backend_url,
                    f"Chat ({uuid.uuid4().hex[:6]})"
                )
                
                if success:
                    backend_session_id = session_data["id"]
                    session_name = session_data["name"]
                    
                    st.session_state.chat_sessions[backend_session_id] = []
                    st.session_state.current_chat_id = backend_session_id
                    st.session_state.session_names[backend_session_id] = session_name
                else:
                    st.error(f"Failed to create session: {session_data}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")
        
        # Display existing chat sessions
        if st.session_state.chat_sessions:
            st.write("Your chats:")
            
            with st.container(height=300):
                for chat_id in st.session_state.chat_sessions.keys():
                    col1, col2 = st.columns([4, 1])
                    
                    display_name = st.session_state.session_names.get(chat_id, chat_id[:6])
                    
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
                                response = requests.delete(f"{backend_url}/sessions/{chat_id}")
                                if response.status_code == 200:
                                    del st.session_state.chat_sessions[chat_id]
                                    if chat_id in st.session_state.session_names:
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
        
        # CSV file upload
        st.markdown("#### Add a new table (CSV)", help="We do not perform any data validation or transformation. Please ensure your CSV is clean and ready for analysis.")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="csv_uploader")
        table_name = st.text_input("Table name", key="table_name_input")
        
        if uploaded_file and table_name:
            if st.button("Upload and Create Table", key="upload_csv_btn"):
                result, success = upload_csv(
                    backend_url,
                    uploaded_file.getvalue(),
                    uploaded_file.name,
                    table_name
                )
                
                if success and result.get("success"):
                    st.success(result.get("message"))
                else:
                    st.error(result.get("message", "Upload failed"))
        
        # Load available providers if not already loaded
        if not st.session_state.providers_loaded:
            providers, success = get_available_providers(backend_url)
            if success:
                st.session_state.providers = providers
                st.session_state.providers_loaded = True