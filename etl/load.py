from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import pandas as pd
from sqlalchemy import create_engine
from contextlib import contextmanager


@contextmanager
def get_db_connection(pg_user, pg_password, airflow=False):
    conn = None
    try:
        conn = psycopg2.connect(
            host="host.docker.internal" if airflow else "localhost",
            database="ticket_trail_db",
            user=pg_user,
            password=pg_password
        )
        yield conn
    finally:
        if conn is not None:
            conn.close()

def load_to_sql(pg_user, pg_password, events=None, event_details=None, venues=None):
    """Load data into PostgreSQL database"""
    try:
        # Use the context manager with 'with' statement
        with get_db_connection(pg_user, pg_password) as conn:
            cursor = conn.cursor()

            # Check if DataFrames are empty
            if events is None and event_details is None and venues is None:
                print('Tables were empty')
                return

            # Load data into the `events` table
            if events is not None:
                print('Loading events')
                for _, row in events.iterrows():
                    cursor.execute("""
                        INSERT INTO events (id, min_ticket_price, date_scraped)
                        VALUES (%s, %s, %s)
                    """, (row['id'], row['min_ticket_price'], row['date_scraped']))
            
            # Load data into the `event_details` table
            if event_details is not None:
                print('Loading event_details')
                for _, row in event_details.iterrows():
                    cursor.execute("""
                        INSERT INTO event_details (event_id, name, genre, event_start_date, 
                                                 public_sales_start, public_sales_end, 
                                                 presale_start, presale_end, tracking, last_tracked)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (event_id) 
                        DO UPDATE SET
                            tracking = EXCLUDED.tracking,
                            last_tracked = EXCLUDED.last_tracked
                    """, (row['event_id'], row['name'], row['genre'], row['event_start_date'], 
                          row['public_sales_start'], row['public_sales_end'], row['presale_start'], 
                          row['presale_end'], row['tracking'], row['last_tracked']))
            
            # Load data into the `venues` table
            if venues is not None:
                print('Loading venues')
                for _, row in venues.iterrows():
                    cursor.execute("""
                        INSERT INTO venues (id, event_id, city, state, venue_name)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) 
                        DO NOTHING           
                    """, (row['id'], row['event_id'], row['city'], row['state'], row['venue_name']))
            
            conn.commit()
            print('Loaded all tables')

    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise  # Re-raise the exception after printing it