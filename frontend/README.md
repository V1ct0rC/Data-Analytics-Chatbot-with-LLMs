## Data-Analytics-Chatbot-with-LLMs (Interface)
This directory contains the frontend components of the Data Analytics Chatbot with LLMs project. The frontend is built using Streamlit, a Python framework for creating data applications with minimal code.

Streamlit was chosen as the UI framework for this project due to its simplicity and rapid development capabilities for data applications. While Streamlit offers impressive functionality with minimal code, it does have limitations in terms of UI customization compared to frameworks like React or Vue.js.

The interface follows Streamlit's standard design patterns and widgets, which restricts some aspects of visual styling and layout control. However, extensive UI customization wasn't a primary focus of this project.

### Architecture
The frontend is structured to separate concerns into different modules and UI components, making it easier to maintain and extend. Below is the directory structure:

```plaintext
frontend/
├── app.py                # Main entry point for the Streamlit app
├── modules/              # Utility modules
│   ├── api.py            # API functions to communicate with backend
│   └── utils.py          # Session state management and utilities
├── ui/                   # UI components
│   ├── chat.py           # Chat interface components
│   ├── landing_page.py   # Landing page UI
│   └── sidebar.py        # Sidebar UI with session management
└── assets/               # Static assets (images, etc.)
```

### Configuration
The frontend can be run independently with the command below. However it's always recommended to use the project's main entry point.

```bash
streamlit run app.py
```

The frontend communicates with the FastAPI backend through the functions defined in api.py, which handles API requests and responses. The UI components are organized into separate files for better maintainability and readability. The frontend connects to the backend using the BACKEND_URL environment variable, which defaults to http://127.0.0.1:8000 (in case of local startup) if not specified.

To add new UI components:

1. Create a new file in the ui/ directory
2. Implement your component as a function that accepts necessary parameters
3. Import and use the component in app.py or other UI files

### Suggested Improvements
- UI Customization: While Streamlit provides a good starting point, consider using a more customizable framework like React or Vue.js for advanced UI features.
- State Management: Implement a more robust state management solution for complex interactions.
- Testing: Add unit tests for UI components to ensure reliability and maintainability.
