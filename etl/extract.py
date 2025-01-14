import pandas as pd
from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine
from typing import Optional

def search_event(key: str, keyword: str, city: Optional[str] = None):
    """
    Search for an event using the Ticketmaster API.
    """
    try:
        url = 'https://app.ticketmaster.com/discovery/v2/events.json'
        params = {
            "apikey": key,
            "keyword": keyword,
            "countryCode": "US",
            "city": city,
            "size": 1
        }

        # Make API call with timeout
        response = requests.get(url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code != 200:
            print(f"API request failed with status code: {response.status_code}")
            return None, None, None
        
        data = response.json()
        
        # Check if search was valid
        if '_embedded' not in data:
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

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None, None, None

def track_current_events(airflow=False, **kwargs):
    """
    Gets most recent prices of events that are currently being tracked.
    
    Args:
        airflow: True if running in Airflow, False if running locally
        kwargs: Keyword arguments (needed for Airflow)
    
    Returns:
        Tuple of (events_df, event_details_df)
    """
    # Load environment variables
    load_dotenv(dotenv_path='/opt/airflow/.env')
    api_key = os.getenv('CONSUMER_KEY')
    pg_user = os.getenv('POSTGRESQL_USER')
    pg_password = os.getenv('POSTGRESQL_PASSWORD')

    # Create database connection
    if airflow:
        host_name = 'host.docker.internal:5432'
    else:
        host_name = 'localhost'
    
    engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@{host_name}/ticket_trail_db")

    # Get events that are being tracked
    event_details_tracking_df = pd.read_sql('SELECT * FROM event_details WHERE tracking = 1', con=engine)
    
    # Prepare lists to store results
    events = []
    failed_events = []  # New: Track any events that fail to update
    
    # Update last_tracked date for all events
    current_date = datetime.now().strftime('%Y-%m-%d')
    event_details_tracking_df['last_tracked'] = current_date

    # Get latest prices for each event
    for event_id in event_details_tracking_df['event_id'].unique(): 
        try:
            # Set up API call
            url = f"https://app.ticketmaster.com/discovery/v2/events/{event_id}.json"
            params = {
                'apikey': api_key,  # Fixed: using api_key instead of key
                'id': event_id
            }

            # Make API call 
            response = requests.get(url, params, timeout=10)  # Added timeout
            
            if response.status_code == 200:
                data = response.json()
                
                # Get current price
                min_ticket_price = data['priceRanges'][0]['min']
                
                # Create event dictionary
                events_dict = {
                    'id': event_id,
                    'min_ticket_price': min_ticket_price,
                    'date_scraped': current_date
                }
                
                # Add to events list
                events.append(events_dict)
            else:
                print(f"Failed to get data for event {event_id}. Status code: {response.status_code}")
                failed_events.append(event_id)
                
        except Exception as e:
            print(f"Error processing event {event_id}: {str(e)}")
            failed_events.append(event_id)
    
    # Convert results to DataFrame
    if events:  # Only create DataFrame if we have events
        events_df = pd.DataFrame(events)
    else:
        events_df = pd.DataFrame()  # Empty DataFrame if no successful updates
    
    # If running in Airflow, push to XCom
    if airflow and 'ti' in kwargs:
        kwargs['ti'].xcom_push(key='events', value=events_df)
        kwargs['ti'].xcom_push(key='events_details', value=event_details_tracking_df)
    
    # Print summary
    print(f"Successfully updated {len(events)} events")
    if failed_events:
        print(f"Failed to update {len(failed_events)} events: {failed_events}")

    return events_df, event_details_tracking_df
  
