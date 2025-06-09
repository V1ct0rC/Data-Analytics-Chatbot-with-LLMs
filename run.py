import subprocess
import os
import signal
import sys
import logging


if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/database_operations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_backend():
    # Run uvicorn from root dir, using full module path
    return subprocess.Popen(
        ["uvicorn", "backend.app.main:app", "--reload"]
    )

def run_frontend():
    # Run streamlit from root dir in headless mode
    return subprocess.Popen(
        ["streamlit", "run", ".\\frontend\\app.py", "--server.headless", "true"]
    )

def run_create_database():
    # Run the database creation script
    return subprocess.call(
        [sys.executable, ".\\cloud\\create_database.py"]
    )

def run_set_default_table():
    # Run the script to set the default table
    return subprocess.call(
        [sys.executable, ".\\cloud\\set_default_table.py"]
    )

if __name__ == "__main__":
    if "--create" in sys.argv:
        logger.info("Running database creation script...")
        run_create_database()
    else:
        logger.info("Running table setup...")
        run_set_default_table()
        backend_proc = run_backend()
        frontend_proc = run_frontend()
        try:
            backend_proc.wait()
            frontend_proc.wait()
        except KeyboardInterrupt:
            backend_proc.send_signal(signal.SIGINT)
            frontend_proc.send_signal(signal.SIGINT)