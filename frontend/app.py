import streamlit as st
import requests
import uuid
import os


st.set_page_config(page_title="Data Analysis Chatbot", layout="wide")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# Initialize session states
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

def start_chatting():
    """Callback to hide the landing page and show the chat interface."""
    st.session_state.show_landing_page = False

# Display landing page
if st.session_state.show_landing_page:
    st.title("Welcome to the Data Analysis Chatbot")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
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
        # Placeholder for an image or illustration
        pass
        
else:
    # Sidebar for chat session management ------------------------------------------------------------------
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
                        del st.session_state.chat_sessions[chat_id]
                        if hasattr(st.session_state, "session_names"):
                            del st.session_state.session_names[chat_id]
                        
                        if chat_id in st.session_state.chart_history:
                            del st.session_state.chart_history[chat_id]
                        
                        if chat_id == st.session_state.current_chat_id:
                            st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
                        st.rerun()
                
        else:
            st.info("No chats yet. Click 'New Chat' to start.")
        
        st.divider()

    # Main chat area ---------------------------------------------------------------------------------------
    st.title("Data Analysis Chatbot")

    if st.session_state.current_chat_id is None or not st.session_state.chat_sessions:
        st.info("👈 Click the 'New Chat' button in the sidebar to start a conversation.")

    else:
        chat_col, viz_col = st.columns([2, 1])

        with chat_col:
            chat_container = st.container(height=800)
            st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)  # Spacer
            input_container = st.container()

            # Get and display current chat messages ----------------------------------------------------------------
            current_messages = st.session_state.chat_sessions[st.session_state.current_chat_id]

            with chat_container:
                st.markdown("""
                <style>
                [data-testid="stVerticalBlock"] {
                    max-height: 800px;
                    overflow-y: auto;
                }
                </style>
                """, unsafe_allow_html=True)

                for message in current_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Input field for user messages ------------------------------------------------------------------------
            with input_container:
                if "submit_pressed" not in st.session_state:
                    st.session_state.submit_pressed = False
                
                def handle_input():
                    """Handle user input submission."""
                    if st.session_state.user_input:
                        # Add user message to chat history
                        current_messages.append({"role": "user", "content": st.session_state.user_input})
                        
                        st.session_state.submit_pressed = True
                
                with st.form(key="message_form", clear_on_submit=True):
                    user_input = st.text_input("Ask a question about your data:",
                                            key="user_input")
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
            st.subheader("Visualizations")
            
            current_session_id = st.session_state.current_chat_id
            session_charts = st.session_state.chart_history.get(current_session_id, [])
            
            if not session_charts:
                st.info("No visualizations yet. Ask for a chart to see visualizations here.")
            else:
                for i, chart_data in enumerate(session_charts):
                    if chart_data["success"]:
                        with st.container():
                            st.markdown(f"### {chart_data['title']}")
                            
                            import pandas as pd
                            df = pd.DataFrame(chart_data["data"])
                            
                            if chart_data["chart_type"] == "bar":
                                st.bar_chart(df, x=chart_data["x_column"], y=chart_data["y_column"])
                                    
                            elif chart_data["chart_type"] == "line":
                                st.line_chart(df, x=chart_data["x_column"], y=chart_data["y_column"])
                                
                            elif chart_data["chart_type"] == "scatter":
                                st.scatter_chart(df, x=chart_data["x_column"], y=chart_data["y_column"])
                        
                            if i < len(session_charts) - 1:
                                st.divider()
                            
                            st.download_button(
                                f"Download data",
                                df.to_csv(index=False).encode('utf-8'),
                                f"{chart_data['title'].lower().replace(' ', '_')}.csv",
                                "text/csv",
                                key=f"download_{i}"
                            )
