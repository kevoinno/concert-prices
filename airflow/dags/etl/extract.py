import pandas as pd
from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine

def search_event(key, keyword, city=None):
    """
    User inputs the keyword and city of event 
    Outputs search results about event in json format. Returns None if API call failed
    """
    url = 'https://app.ticketmaster.com/discovery/v2/events.json'

    params = {
    "apikey" : key,
    "keyword" : keyword,
    "countryCode" : "US",
    "city" : city,
    "size" : 1
    }

    # Make API call
    response = requests.get(url, params)
    if response.status_code == 200:
        data = response.json()
        with open("response.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    else:
        print(f"API Call failed. Response Status Code {response.status_code}")
        return None, None, None
    
    # Check if search was valid
    if data.get('_embedded', -1) == -1:
        print('Search had no results')
        return None, None, None

    # Extract info for events
    events = []
    event_details = []
    venues = []

    for event in data['_embedded']['events']:
        # Pulling data for events table
        event_id = event.get('id', None)
        min_ticket_price = event['priceRanges'][0].get('min', 0)
        date_scraped = datetime.now().strftime('%Y-%m-%d')

        # Pulling data for the event_details table
        event_start_date = event['dates']['start']['dateTime']
        event_name = event.get('name', None)
        genre = event['classifications'][0]['genre']['name']
        public_sales_start = event['sales']['public']['startDateTime']
        public_sales_end = event['sales']['public']['endDateTime']
        # Check if there were presales and get the earliest and latest presale date
        presales = event['sales'].get('presales', None)
        if presales:
            presale_start_dates = []
            presale_end_dates = []
            for p in presales:
                presale_start_dates.append(p['startDateTime'])
                presale_end_dates.append(p['endDateTime'])
            presale_start = min(presale_start_dates)
            presale_end = min(presale_end_dates)
        else:
            presale_start = None
            presale_end = None

        # Pulling data for the venues table
        venue_id = event['_embedded']['venues'][0]['id']
        venue_name = event['_embedded']['venues'][0]['name']
        city = event['_embedded']['venues'][0]['city']['name']
        state = event['_embedded']['venues'][0]['state']['stateCode']


        # Put all results in a dictionary
        event_dict = {
            'id' : event_id,
            'min_ticket_price' : min_ticket_price,
            'date_scraped' : date_scraped
        }

        event_details_dict = {
            'event_id' : event_id,
            'name' : event_name,
            'genre' : genre,
            'event_start_date' : event_start_date,
            'public_sales_start' : public_sales_start,
            'public_sales_end' : public_sales_end,
            'presale_start' : presale_start,
            'presale_end' : presale_end,
            'tracking' : 1 if date_scraped <= event_start_date else 0, # 1 if currently tracking 0 if not
            'last_tracked' : date_scraped
        }

        venues_dict = {
            'event_id' : event_id,
            'city' : city,
            'state' : state,
            'venue_name' : venue_name,
            'id' : venue_id
        }


        # Add to list
        events.append(event_dict)
        event_details.append(event_details_dict)
        venues.append(venues_dict)

        # Convert ot dataframe
        events_df = pd.DataFrame(events)
        events_details_df = pd.DataFrame(event_details)
        venues_df = pd.DataFrame(venues)
    return events_df, events_details_df, venues_df

def track_current_events(airflow=False, **kwargs):
    """
    Gets most recent prices of the events that are currently being tracked (tracking = 1 in the event_details table) 
    User inputs api key, user id for PostgreSQL database, and password for PostgreSQL database
    Returns a events pandas dataframes of the up-to-date prices for the tracked events

    Note: if airflow = True the engine connection string will refer to the host machine. Use this when you are calling this function in the Airflow DAG, since Airflow is running in Docker
    
    TEMPORARILIY DELETED key, pg_user, pg_password from function arguments
    """
    # Load environment variables
    load_dotenv(dotenv_path='/opt/airflow/.env')
    api_key = os.getenv('CONSUMER_KEY')
    pg_user = os.getenv('POSTGRESQL_USER')
    pg_password = os.getenv('POSTGRESQL_PASSWORD')

    print(f"DEBUG: Postgres User: {pg_user}, Password: {pg_password}")

    # Create engine
    if airflow:
        host_name = 'host.docker.internal:5432'
    else:
        host_name = 'localhost'
    engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@{host_name}/ticket_trail_db")

    # Get event_id's of events that are currently being tracked
    event_details_tracking_df = pd.read_sql('SELECT * FROM event_details WHERE tracking = 1', con = engine)
    
    # Get most recent ticket prices for these events
    events = []
    event_details_tracking_df['last_tracked'] = datetime.now().strftime('%Y-%m-%d')
    

    for id in event_details_tracking_df['event_id'].unique(): 
        # Specify url and params for API call
        url = f"https://app.ticketmaster.com/discovery/v2/events/{id}.json"
        params = {
            'apikey' : key,
            'id' : id
        }

        # Make API call 
        response = requests.get(url, params)
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"API Call failed. Response Status Code {response.status_code}")
            return None, None, None
        
        # Get info for events table
        min_ticket_price = data['priceRanges'][0]['min']
        date_scraped = datetime.now().strftime('%Y-%m-%d')

        events_dict = {
            'id' : id,
            'min_ticket_price' : min_ticket_price,
            'date_scraped' : date_scraped
        }

        # Add to list
        events.append(events_dict)
        
        # Convert to dataframe
        events_df = pd.DataFrame(events)

        # Push dataframes to XComs for Airflow
        kwargs['ti'].xcom_push(key='events', value = events_df)
        kwargs['ti'].xcom_push(key='events_details', value = event_details_tracking_df)

    return events_df, event_details_tracking_df
  
