
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import pandas as pd
from sqlalchemy import create_engine


def load_to_sql(pg_user, pg_password, events=None, event_details=None, venues=None):

    # Step 1: Connect to the database
    conn = psycopg2.connect(
        host="localhost",
        database="ticket_trail_db",
        user=pg_user,
        password=pg_password
    )
    cursor = conn.cursor()

    # Step 2: Check if DataFrames are empty
    if events is None and event_details is None and venues is None:
        print('Tables were empty')
        return

    # Step 3: Load data into the `events` table
    if events is not None:
        print('Loading events')
        for _, row in events.iterrows():
            cursor.execute("""
                INSERT INTO events (id, min_ticket_price, date_scraped)
                VALUES (%s, %s, %s)
            """, (row['id'], row['min_ticket_price'], row['date_scraped']))
    
    # Step 4: Load data into the `event_details` table
    if event_details is not None:
        print('Loading event_details')
        for _, row in event_details.iterrows():
            cursor.execute("""
                INSERT INTO event_details (event_id, name, genre, event_start_date, public_sales_start, public_sales_end, presale_start, presale_end, tracking, last_tracked)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) 
                DO UPDATE SET
                    tracking = EXCLUDED.tracking,
                    last_tracked = EXCLUDED.last_tracked
            """, (row['event_id'], row['name'], row['genre'], row['event_start_date'], row['public_sales_start'], row['public_sales_end'], row['presale_start'], row['presale_end'], row['tracking'], row['last_tracked']))
    
    # Step 5: Load data into the `venues` table
    if venues is not None:
        print('Loading venues')
        for _, row in venues.iterrows():
            cursor.execute("""
                INSERT INTO venues (id, event_id, city, state, venue_name)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) 
                DO NOTHING           
            """, (row['id'], row['event_id'], row['city'], row['state'], row['venue_name']))
    
    # Step 6: Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    print('Loaded all tables')

def load_to_sql_airflow(pg_user, pg_password, **kwargs):
    # Step 1: Connect to the database and pull data from Xcoms
    conn = psycopg2.connect(
        host="localhost",
        database="ticket_trail_db",
        user=pg_user,
        password=pg_password
    )
    cursor = conn.cursor()

    ti = kwargs['ti']
    events = ti.xcom_pull(task_ids='track_prices', key = 'events')
    event_details = ti.xcom_pull(task_ids='track_prices', key ='event_details')

    # Step 2: Check if DataFrames are empty
    if events is None and event_details is None:
        print('Tables were empty')
        return

    # Step 3: Load data into the `events` table
    if events is not None:
        print('Loading events')
        for _, row in events.iterrows():
            cursor.execute("""
                INSERT INTO events (id, min_ticket_price, date_scraped)
                VALUES (%s, %s, %s)
            """, (row['id'], row['min_ticket_price'], row['date_scraped']))
    
    # Step 4: Load data into the `event_details` table
    if event_details is not None:
        print('Loading event_details')
        for _, row in event_details.iterrows():
            cursor.execute("""
                INSERT INTO event_details (event_id, name, genre, event_start_date, public_sales_start, public_sales_end, presale_start, presale_end, tracking, last_tracked)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) 
                DO UPDATE SET
                    tracking = EXCLUDED.tracking,
                    last_tracked = EXCLUDED.last_tracked
            """, (row['event_id'], row['name'], row['genre'], row['event_start_date'], row['public_sales_start'], row['public_sales_end'], row['presale_start'], row['presale_end'], row['tracking'], row['last_tracked']))
    
    # Step 5: Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    print('Loaded all tables')
