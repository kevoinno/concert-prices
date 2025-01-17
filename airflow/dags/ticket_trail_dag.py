from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import sys

# Add the path BEFORE importing etl modules
sys.path.append('/home/kevin/concert-prices')

# Now we can import from etl
from etl.extract import track_current_events
from etl.transform import transform
from etl.load import load_to_sql

# Load environment variables
load_dotenv()

# Define default arguments
default_args = {
    'owner': 'your_name',
    'retries': 1,
    'retry_delay': timedelta(seconds = 10),
    'start_date': datetime.now()
}

# Create DAG
dag = DAG(
    'ticket_trail',
    default_args=default_args,
    description='Track ticket prices daily',
    schedule_interval='@daily',
    catchup=False
)

# Split into separate tasks
def extract():
    events_df, event_details_df = track_current_events()
    return {
        'events_df': events_df,
        'event_details_df': event_details_df
    }

def load(ti):
    # Get DataFrames from previous task
    data = ti.xcom_pull(task_ids='extract_task')
    if not data:
        raise ValueError("No data received from extract task")
    
    # Load credentials using absolute path
    env_path = '/home/kevin/concert-prices/.env'
    load_dotenv(env_path)
    pg_user = os.getenv('POSTGRESQL_USER')
    pg_password = os.getenv('POSTGRESQL_PASSWORD')
    
    # Debug prints
    print(f"User: {pg_user}")
    print(f"Password: {pg_password}")
    
    load_to_sql(pg_user, pg_password, data['events_df'], data['event_details_df'])

# Create separate tasks
extract_task = PythonOperator(
    task_id='extract_task',
    python_callable=extract,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_task',
    python_callable=load,
    dag=dag
)

# Set task dependencies
extract_task >> load_task