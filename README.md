# Data-Analytics-Chatbot-with-LLMs
This repository contains implementations for a data analytics chatbot with LLMs. The chatbot is able to interpret queries made in natural language to a dataset, translate them into appropriate operations on a cloud-based database, and return meaningful insights from a given dataset.

![Landing Page](frontend/assets/landing_page_print.png)

![Chat Session](frontend/assets/chat_session_print.png)

![Chat Providers](frontend/assets/chat_providers_print.png)

## Architecture Overview
This repo is divided into three main parts: the frontend, the backend and the cloud. The frontend is responsible for the user interface, while the backend handles the logic of processing user queries, interacting with the database, and generating responses. The cloud part is responsible for creatng the infrascructure and hosting the database and making it accessible to the backend.

```bash
Data-Analytics-Chatbot-with-LLMs/
├── backend/
│   └── app/
│       ├── main.py
│       ├── ... (other backend files)
│       └── llm/
│           ├── factory.py
│           ├── prompt_templates.py
│           └── providers/
│               ├── base.py
│               └── ... (other LLM providers)
├── cloud/
│   ├── create_database.py
│   └── set_default_table.py
├── frontend/
│   ├── app.py
│   ├── modules/
│   │   ├── api.py
│   │   └── ... (other system modules)
│   ├── ui/
│   │   ├── landing_page.py
│   │   └── ... (other UI components)
│   └── assets/
│       ├── landing_page_print.png
│       └── ... (other asset files)
├── .env
├── requirements.txt
├── run.py
└── README.md
```

As everything was made using Python, I could have avoided this division between front and backend, but I wanted to create a more modular and scalable architecture, similar to real-world web applications. This way, the frontend can be easily replaced or updated without affecting the backend logic, and vice versa.

For the frontend, I used [Streamlit](https://streamlit.io/), a powerful framework for building data applications. The backend is built with Python (FastAPI), using libraries such as [SQLAlchemy](https://www.sqlalchemy.org/) for database interactions. The cloud part is implemented using [AWS RDS](https://aws.amazon.com/rds/) for hosting the database, and [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for interacting with AWS services.

The main LLM provider used in this project is [Google Gemini](https://ai.google.dev/gemini), which provides powerful language models that can understand and generate natural language text. The models are used to interpret user queries, translate them into SQL queries, and generate responses based on the results of the queries. Gemini was chosen because it seamlessly integrates with Python functions and have a robust API for interacting with the backend.

Along with the main LLM provider, I also implemented a factory pattern to allow for easy integration of other LLM providers in the future. This way, the chatbot can be easily extended to support multiple LLM providers without changing the core logic of the application. As an example, I added another provider, [Groq](https://groq.com/), by just creating a new file in the `llm/providers/`.

> For more details about each part of the project, please refer to the respective directories: `frontend/`, `backend/`, and `cloud/`. They all contain their own README files with more information about the implementation, design choices, and improvements that can be made. I **STRONGLY RECOMMENDED** reading the `backend/README.md` file, as it contains a detailed explanation of the main LLM decisions functionalities.

## Installation and Setup
To run the application, you only need to create a virtual environment with the required dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

You also need to create a `.env` file in the root directory of the project. This file will contain the environment variables needed for the application to run properly. The current state of the code supports two main LLM providers: Google Gemini and Groq. You can choose to use one or both of them by setting the respective environment variables in the `.env` file.

```plaintext
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

Incase you already have a cloud database instantiated (the code was only tested in PostgreSQL), you can add the following environment variable directply to the `.env` file:

```plaintext
DATABASE_URL=your_database_url
```

If you want to create a new AWS RDS cloud database (PostgreSQL), you need add you credencials to the `.env` file:

```plaintext
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION_NAME=your_aws_region

DB_NAME=your_database_name
DB_INSTANCE_IDENTIFIER=your_database_instance_identifier
DB_USERNAME=your_database_master_username
DB_PASSWORD=your_database_master_password
```

Create a new database by running the following command in the terminal:

```bash
python run.py --create
```
A new AWS RDS database will be created, and the `DATABASE_URL` will be automatically updated in the `.env` file.

Without a cloud database or AWS credencials, the code will automatically use a local SQLite database. With all set, you can run the application via:

```bash
python run.py
```

You will be able to open your browser and access the application at `http://localhost:8501`.

## Comments and Thoughts
Biggest difficulties:
- Organizing the code in a way that is easy to understand and maintain.
- Ensuring that the chatbot can call the right functions with the right parameters based on the user's query, especially when dealing with different LLM providers and their specific requirements.
- Making the conversation context persistent across multiple queries and multiple models, so that any chatbot can provide meaningful responses based on the user's previous queries and continue the conversation seamlessly.
- One of the most challenging part was running all the code together from a single entry point, as the code is divided into multiple files and modules. I had to ensure that all the imports and dependencies were correctly set up, and that the code could be executed in a single run without any issues.
- I got to confess that I do not have much experience with tests. The tests implemented in this project are basic and were created with the help of code assistants (Copilot). Obviously, they were revised and improved by me, but I did not go deep into the testing libraries or best practices. I would like to improve my knowledge in this area and implement more robust tests in the future.

> Is is also worth mentioning that I did use some LLM code assistants to help me with the implementation of the code. However NO CRUCIAL PART OF THE CODE WAS GENERATED BY THEM. They were used mainly to write readme files, comments, hints about code organization and some repetitive code snippets (and to help with tests, as I said before). The main logic and architecture of the application were designed and implemented by me.

---
Future improvements:
- The model does no work so well on newly uploaded datasets, probably because it has no backgroud information about its columns. It would be great to have a way to provide the model with some context about the dataset.
- There is no logic for multiple users, login, or authentication.
- Some details like chat naming and user profile are not implemented.
- The interface look well using streamlit, but it would be great to have a more polished and customizable UI.
- A stronger error handling and validation in backend. I did not go deep into documentation of the libraries used, so there may be some edge cases that are not handled the best way.
- Using a prper cloud infrastructure as code tool like Terraform or AWS CDK to manage the cloud resources.
- Display in a better way the thinking process of the models that support it, especially Deepseek R1, that usually thinks a lot before answering.
- I could have kept the same reurn pattern for the endpoint responses, but I ended implemented them at different times, so they are not consistent across the application. Of course, this does nit affect the functionality.