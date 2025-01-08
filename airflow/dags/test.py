from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='/opt/airflow/.env')
api_key = os.getenv('CONSUMER_KEY')
pg_user = os.getenv('POSTGRESQL_USER')
pg_password = os.getenv('POSTGRESQL_PASSWORD')

print(api_key)
print(pg_user)
print(pg_password)

engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@host.docker.internal:5432/ticket_trail_db")

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
