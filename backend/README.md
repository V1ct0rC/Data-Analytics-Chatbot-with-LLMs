## Data-Analytics-Chatbot-with-LLMs (Backend)
This directory contains the backend components of the Data Analytics Chatbot with LLMs project. The backend provides API endpoints for managing chat sessions, executing database queries, and generating AI responses using various LLM providers.

### Architecture
The backend is built with FastAPI and follows a modular, layered architecture to promote separation of concerns and maintainability. Below is the directory structure of the backend:

```plaintext
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── db/                     # Database related code
│   │   ├── models.py           # Pydantic models for API requests/responses
│   │   └── db_functions.py     # Database utility functions
│   └── llm/                    # LLM integration code
│       ├── factory.py          # Factory pattern for LLM providers
│       ├── session.py          # Chat session management
│       ├── agent_functions.py  # Database query & chart generation functions
│       ├── prompt_templates.py # System prompts for LLM providers
│       └── providers/          # LLM provider implementations
│           ├── base.py         # Abstract base class for providers
│           ├── gemini.py       # Google Gemini implementation
│           └── groq.py         # Groq implementation
└── tests/
    └── backend_tests.py        # Unit tests
```

### Design Choices
FastAPI was chosen as the backend framework for this project due to its exceptional combination of performance, developer experience, and features tailored for modern API development. It is also extremely easy to set up and, personally, I was more familiar with it compared to other frameworks like Flask or Django.

The backend implements a factory pattern via the LLMProviderFactory class to manage different LLM providers.This design choice enables:
- Easy addition of new LLM providers with minimal code changes. given by the factory pattern `LLMProviderFactory`.
- Dynamic provider selection at runtime.
- Consistent interface for interacting with different LLMs garanteed by the abstract base class `LLMProvider`.

The backend also implements function calling capabilities for LLMs, allowing them to:
- Execute SQL queries against the database.
- Generate charts based on data.
- List available tables.

This powerful feature lets the AI access and analyze data directly.

The backend supports both PostgreSQL (for production) and SQLite (for local development), enabeling easy testing and development without requiring cloud access. The database connection is managed through SQLAlchemy, which provides a robust ORM layer.

### Configuration
To fully utilize the backend, you need to set up the environment variables for the LLM providers and database connection. The required environment variables are:

```plaintext	
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_database_url (or local SQLite file path)
```

"llama-3.3-70b-versatile", "qwen-qwq-32b", "deepseek-r1-distill-llama-70b"

The models supported by the code so far are:
- Google Gemini: `gemini-2.0-flash` (The default model and the one I most tested)
- Google Gemini: `gemini-1.5-flash` (Does not seem to deal with function calling very well)
- Google Gemini: `gemini-1.5-pro` (May not be available for all users, depends on your API free tier usage)
- Groq: `llama-3.3-70b-versatile` (Was also tested, but not as extensively as Gemini. Works well with function calling)
- Groq: `qwen-qwq-32b` (Also works well with function calling, has thinking capabilities)
- Groq: `deepseek-r1-distill-llama-70b` (Works well and also has thinking capabilities)

The backend can be run independently with the command below. However, it's always recommended to use the project's main entry point.

```bash
uvicorn app.main:app --host
```

### Suggested Improvements
- Add streaming responses for LLMs that support it
- Add authentication and user management
- Implement caching for frequently executed queries
- Add comprehensive unit and integration tests
- Support for more LLM providers
- Improve error handling and logging
