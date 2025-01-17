"""
Steps
1. Create connection
2. Create Cursor
3. Create database
4. New connection to db
5. Create tables
6. Commit + Close
"""


from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Get environment variables
load_dotenv()
pg_user = os.getenv('POSTGRESQL_USER')
pg_password = os.getenv('POSTGRESQL_PASSWORD')
pg_host = os.getenv('POSTGRESQL_HOST')

print(f"Host: {pg_host}")
print(f"User: {pg_user}")
print(f"Password: {pg_password}")
print("Attempting to connect to PostgreSQL...")

# Before first connection
print("Creating initial connection...")
pgconn = psycopg2.connect(
    host = pg_host,
    port = '5432',
    user = pg_user,
    password = pg_password,
    database = 'postgres'
)

print("Connection successful!")

# Create cursor
pgcursor = pgconn.cursor()

# required code
pgconn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)


# Drop and Create DB
pgcursor.execute('DROP DATABASE IF EXISTS ticket_trail_db')
pgcursor.execute('CREATE DATABASE ticket_trail_db')

# Commit & Close
pgconn.commit()
pgconn.close()


# Connect to ticket trail db
pgconn = psycopg2.connect(
    host = pg_host,
    port = '5432',
    user = pg_user,
    password = pg_password,
    database = 'ticket_trail_db'
)

# Create cursor
pgcursor = pgconn.cursor()

# required code
pgconn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create events, event_details, venues tables
pgcursor.execute("""

CREATE TABLE IF NOT EXISTS events
(
    id VARCHAR(50), 
    min_ticket_price FLOAT,
    date_scraped DATE
);

""")

pgcursor.execute("""
                 
CREATE TABLE IF NOT EXISTS event_details
(
    id SERIAL,
    event_id VARCHAR(50) PRIMARY KEY, 
    name VARCHAR(100),
    genre VARCHAR(50),
    event_start_date DATE,
    public_sales_start DATE,
    public_sales_end DATE,
    presale_start DATE,
    presale_end DATE,
    tracking INT,
    last_tracked DATE
);

""")

pgcursor.execute("""

CREATE TABLE IF NOT EXISTS venues
(
    id VARCHAR(50) PRIMARY KEY,
    event_id VARCHAR(50),
    city VARCHAR(50),
    state VARCHAR(2),
    venue_name VARCHAR(100)
);

""")

# Commit & Close
pgconn.commit()
pgconn.close()