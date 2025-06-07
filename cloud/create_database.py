import boto3
import os
from dotenv import load_dotenv


load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME", None)

DB_NAME = os.getenv("DB_NAME", "myautodatabase")
DB_INSTANCE_IDENTIFIER = os.getenv("DB_INSTANCE_IDENTIFIER", "myautodbinstance")
DB_USERNAME = os.getenv("DB_USERNAME", "db_username")
DB_PASSWORD = os.getenv("DB_PASSWORD", "db_password")

def create_rds_database(db_name: str, db_instance_identifier: str, db_username: str, db_password: str) -> dict:
    """
    Create an RDS database instance.

    Args:
        db_name: Name of the database to create.
        db_instance_identifier: Unique identifier for the RDS instance.
        db_username: Master username for the database.
        db_password: Master password for the database.

    Returns:
        dict: Response from the RDS create_db_instance call.
    """
    rds_client = boto3.client(
        'rds', aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME
    )

    # Check if the RDS instance already exists
    try:
        response = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
        print(f"RDS instance {db_instance_identifier} already exists.")
        return response['DBInstances'][0]
    
    except rds_client.exceptions.DBInstanceNotFoundFault:
        print(f"Creating new RDS instance: {db_instance_identifier}")

    waiter = rds_client.get_waiter('db_instance_available')

    response = rds_client.create_db_instance(
        DBName=db_name,
        DBInstanceIdentifier=db_instance_identifier,
        AllocatedStorage=20,
        DBInstanceClass='db.t4g.micro',
        Engine='postgres',
        MasterUsername=db_username,
        MasterUserPassword=db_password,
        BackupRetentionPeriod=7,
        PubliclyAccessible=True
    )
    # Wait for the DB instance to be available
    waiter.wait(DBInstanceIdentifier=db_instance_identifier)

    url = f"postgresql+psycopg2://{db_username}:{db_password}@{response['DBInstance']['Endpoint']['Address']}:{response['DBInstance']['Endpoint']['Port']}/{db_name}"
    return url


def get_database_url() -> str:
    """
    Get the right database URL (local or AWS RDS).
    NOT USED. It would require aws credentials all the time.
    
    Returns:
        str: The database URL.
    """
    DATABASE_URL = os.getenv("DATABASE_URL", None)

    if not AWS_ACCESS_KEY or not AWS_SECRET_ACCESS_KEY or not AWS_REGION_NAME:
        print("AWS credentials or region not set in environment variables. Using local SQLite database.")
        return "sqlite:///app.db"
    
    rds_client = boto3.client(
        'rds', aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME
    )

    if not DATABASE_URL:
        print("DATABASE_URL not set. Using local SQLite database.")
        return "sqlite:///app.db"
    
    elif DATABASE_URL.startswith("postgresql+psycopg2://"):
        # check if the RDS instance is available
        try:
            response = rds_client.describe_db_instances()
            for db_instance in response['DBInstances']:
                if db_instance['DBInstanceIdentifier'] in DATABASE_URL:
                    print("Using AWS RDS PostgreSQL database.")
                    return DATABASE_URL
                
        except rds_client.exceptions.DBInstanceNotFoundFault:
            raise ValueError("RDS instance not found. Please check your DATABASE_URL.")
    
    else:
        print("Using local SQLite database.")
        return "sqlite:///app.db"


if __name__ == "__main__":
    db_name = DB_NAME
    db_instance_identifier = DB_INSTANCE_IDENTIFIER
    db_username = DB_USERNAME
    db_password = DB_PASSWORD

    if not AWS_ACCESS_KEY or not AWS_SECRET_ACCESS_KEY or not AWS_REGION_NAME:
        raise ValueError("AWS credentials or region not set in environment variables.")

    try:
        db_url = create_rds_database(db_name, db_instance_identifier, db_username, db_password)
        print(f"Database created successfully: {db_url}")

        # Write or update DATABASE_URL in .env
        env_path = ".env"
        lines = []
        found = False
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        lines.append(f"DATABASE_URL={db_url}\n")
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append(f"DATABASE_URL={db_url}\n")
        with open(env_path, "w") as f:
            f.writelines(lines)
    except Exception as e:
        print(f"Error creating database: {e}")