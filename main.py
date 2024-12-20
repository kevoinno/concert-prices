from etl.extract import search_event
from etl.transform import transform
from etl.load import load_to_sql
import pandas as pd
import os
from dotenv import load_dotenv

def main():
   
   # Load in API keys
    load_dotenv()
    api_key = os.getenv('CONSUMER_KEY')
    pg_user = os.getenv('POSTGRESQL_USER')
    pg_password = os.getenv('POSTGRESQL_PASSWORD')

    # get user's keyword
    user_keyword = input("Enter a artist or concert: ")
    if len(user_keyword) == 0:
        print('No input given')
        return
    # search the event
    events_df, event_details_df, venues_df = search_event(keyword = user_keyword, key = api_key)

    # transform the tables
    events_df, event_details_df, venues_df = transform(events_df, event_details_df, venues_df)
    
    # load dataframes into SQL
    load_to_sql(events_df, event_details_df, venues_df, pg_user, pg_password)

if __name__ == '__main__':
      main()
