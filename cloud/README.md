## Data-Analytics-Chatbot-with-LLMs (Cloud)
This directory contains the cloud infrastructure components for the Data Analytics Chatbot with LLMs project. These scripts handle database provisioning, configuration, and data initialization.

### Design Choices
The project implements a flexible approach to database connectivity, allowing seamless switching between local development and cloud deployment. The application uses the AWS SDK for Python (boto3) to authenticate ans use AWS services.

Throughout the codebase, SQLAlchemy engines were used to manage database connections, enabling support for both PostgreSQL (on AWS RDS) and SQLite (for local development). This design choice allows developers to work with a local SQLite database during development and testing, while still being able to deploy to a cloud-based PostgreSQL database when needed.

The exact same code works for both SQLite and PostgreSQL because SQLAlchemy abstracts away the differences between database approaches. SQLAlchemy engines handle connection pooling, resource management, and cleanup. The project also uses SQLAlchemy's exception handling for consistent error management.

Afterall, this SQLAlchemy engine setup enables:
- Development Flexibility: Developers can work locally with SQLite without AWS credentials
- Production Readiness: The same code deploys to a cloud PostgreSQL database
- Testing Simplicity: Tests can run against a temporary SQLite database
- Consistent Interface: Database interactions use the same patterns regardless of the backend
- Seamless Transitions: Moving from development to production requires only changing an environment variable

### Configuration
To use the cloud database functionality, set the following environment variables in your .env file:
```plaintext
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION_NAME=your_aws_region

DB_NAME=your_database_name
DB_INSTANCE_IDENTIFIER=your_database_identifier
DB_USERNAME=your_database_username
DB_PASSWORD=your_database_password
```

To create a new AWS RDS database instance:
```bash
python cloud/create_database.py
```

To initialize the database schema and load default data:
```bash
python cloud/set_default_table.py
```

After creating a database, the DATABASE_URL will be automatically added to your .env file:
```plaintext
DATABASE_URL=postgresql+psycopg2://username:password@hostname:port/dbname
```

Without cloud credentials, the system automatically uses a local SQLite database (app.db). This allows for development and testing without AWS access.

### Database Schema
The scripts create the following tables:

- clientes: Default data table with customer information
- chat_sessions: Stores chat session metadata
- chat_messages: Stores individual messages within chat sessions

### Suggested Improvements
This implementation uses basic scripts and is far from production-ready. Consider the following improvements:
- Use a more robust infrastructure as code tool like Terraform or AWS CDK for better management and scalability.
- The RDS instance is configured as publicly accessible but should be restricted in production environments.
- Consider implementing additional security measures like VPC configuration for production deployments.
- Thise whole process of setting the DATABASE_URL was easy to implement but is far from ideal. It was just made for the sake of simplicity. A better approach would be to use a more robust configuration management system.