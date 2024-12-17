from etl.extract import search_event
from etl.transform import transform
import pandas as pd
import os
from dotenv import load_dotenv

def main():
   
   # Load in API keys
    load_dotenv()
    api_key = os.getenv('CONSUMER_KEY')
    pg_user = os.getenv('POSTGRESQL_USER')
    pg_password = os.getenv('POSTGRESQL_PASSWORD')


    # search the event
    events_df, event_details_df, venues_df = search_event(keyword = 'Sabrina Carpenter', key = api_key)

    # transform the tables
    events_df, event_details_df, venues_df = transform(events_df, event_details_df, venues_df)
    
    print(events_df)
    print('\n')
    print(event_details_df)
    print('\n')
    print(venues_df)

if __name__ == '__main__':
      main()
