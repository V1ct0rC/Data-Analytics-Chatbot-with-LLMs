import streamlit as st
from ast import literal_eval
import pandas as pd
from modules.api import send_message


def parse_y_column(y_column):
    """Parse the y_column input to handle both string and list formats."""
    try:
        return literal_eval(y_column)
    except Exception:
        return y_column

def render_chat_area(backend_url: str) -> None:
    """Render the main chat area where users can interact with the chatbot."""
    st.title("Data Analysis Chatbot")

    if st.session_state.current_chat_id is None or not st.session_state.chat_sessions:
        st.info("👈 Click the 'New Chat' button in the sidebar to start a conversation.")
    else:
        chat_col, viz_col = st.columns([2, 1])

        with chat_col:
            # Display current chat messages
            current_messages = st.session_state.chat_sessions[st.session_state.current_chat_id]
            
            chat_container = st.container(height=450)
            with chat_container:
                for message in current_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # LLM settings and message input
            input_container = st.container()
            with input_container:
                with st.expander("Advanced LLM Settings"):
                    # Provider selection
                    if st.session_state.providers:
                        providers = list(st.session_state.providers.keys())
                        provider = st.selectbox(
                            "Provider", 
                            providers,
                            index=providers.index(st.session_state.current_provider) if st.session_state.current_provider in providers else 0,
                            key="provider_select",
                            help="Select the LLM provider to use for generating responses. The available providers depend on your configuration and API keys."
                        )
                        st.session_state.current_provider = provider
                        
                        # Model selection for current provider
                        if provider in st.session_state.providers and st.session_state.providers[provider]:
                            models = st.session_state.providers[provider]
                            if models:
                                model = st.selectbox(
                                    "Model",
                                    models,
                                    index=0 if st.session_state.current_model not in models else models.index(st.session_state.current_model),
                                    key="model_select",
                                    help="Select the model to use for this provider. The response quality may vary geatly depending on the model selected."
                                )
                                st.session_state.current_model = model
                    
                    # Generation parameters
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
                
                # Message input form
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
                                    result, success = send_message(
                                        backend_url,
                                        user_input,
                                        st.session_state.current_chat_id,
                                        provider=st.session_state.current_provider,
                                        model=st.session_state.current_model,
                                        temperature=temperature,
                                        top_p=top_p,
                                        top_k=top_k
                                    )
                                    
                                    if success:
                                        answer = result["response"]
                                        
                                        # Process chart data if available
                                        if "chart_data" in result and result["chart_data"] and result["chart_data"]["success"]:
                                            session_id = st.session_state.current_chat_id
                                            
                                            if session_id not in st.session_state.chart_history:
                                                st.session_state.chart_history[session_id] = []
                                            
                                            st.session_state.chart_history[session_id].append(result["chart_data"])
                                            st.session_state.current_chart_data = result["chart_data"]
                                    else:
                                        answer = str(result) if result else "Error communicating with backend"
                                    
                                    st.markdown(answer)
                        
                        # Add assistant response to chat history
                        current_messages.append({"role": "assistant", "content": answer})
                        st.rerun()
        
        # Visualization area
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