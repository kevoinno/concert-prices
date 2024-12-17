
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import pandas as pd
from sqlalchemy import create_engine


def load_to_sql(, pg_user, pg_password):
    # Step 1: Create engine
    engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@localhost/ticket_trail_db")

    # Step 2: Add dataframe to SQL
    """
    TO DO: FILL IN WITH df.to_sql for all 3 dataframes
    """