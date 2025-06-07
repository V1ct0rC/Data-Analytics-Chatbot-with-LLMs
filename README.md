# Data-Analytics-Chatbot-with-LLMs
This repository contains implementations for a data analytics chatbot with LLMs. The chatbot is able to interpret queries made in natural language to a dataset, translate them into appropriate operations on a cloud-based database, and return meaningful insights from a given dataset.

![Landing Page](frontend/assets/landing_page_print.png)

---
To run the application locally, you only need to create a `.env` file in the root directory or export the following environment variables in your terminal:

```plaintext
GEMINI_API_KEY=your_gemini_api_key
```

Incase you have a cloud database, you can also add the following environment variables to the `.env` file:

```plaintext
DATABASE_URL=your_database_url

> depending on your database type, you may also need to set the following variables:
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_NAME=your_database_name
DATABASE_HOST=your_database_host
DATABASE_PORT=your_database_port
```

Without a cloud database, the code will automatically use a local SQLite database.

---
```bash
cd .\backend\app\
uvicorn main:app --reload
```

```bash
streamlit run .\frontend\app.py
```

---
Future improvements:
- The model does no work so well on new uploaded datasets, probably because it has no backgroud information about its columns. It would be great to have a way to provide the model with some context about the dataset.
- There is no logic for multiple users, login, or authentication.
- Some details like chat naming and user profile are not implemented.
- The interface look well using streamlit, but it would be great to have a more polished and customizable UI.
- A stronger error handling and validation in backend. I did not go deep into documentation of the libraries used, so there may be some edge cases that are not handled the best way.