from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from etl.extract import track_current_events
from etl.load import load_to_sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='/opt/airflow/.env')

# Access variables
pg_user = os.getenv('POSTGRESQL_USER')
pg_password = os.getenv('POSTGRESQL_PASSWORD')
api_key = os.getenv('CONSUMER_KEY')

print(f"[DEBUG] Postgres User: {pg_user}, Password: {pg_password}, API Key: {api_key}")


default_args = {
    'owner' : 'kevin',
    'depends_on_past' : False,
    'retries' : 1
}

with DAG(
    'concert_pipeline',
    default_args=default_args,
    description='Tracks concert prices searched by users daily until the concert happens',
    schedule_interval='@daily', # how often to run the pipeline
    start_date=datetime(2025,1,5), # when to start running pipeline
    catchup=False # don't run missed schedules
) as dag:
    """
    Steps to pipeline

    1. Extract prices for concert ids in the tracking table. track_current_events() does this
    2. Load them into the database

    Note: Data transformations are not needed in this case
    """
    # Task 1: Extract prices
    task_track_prices = PythonOperator(
        task_id = 'track_prices',
        python_callable = track_current_events,
        op_args = [True],
        provide_context = True
    )



    # Define DAG/task dependencies
    task_track_prices 

