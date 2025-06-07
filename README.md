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
python .\db\default_database.py
uvicorn main:app --reload
```
