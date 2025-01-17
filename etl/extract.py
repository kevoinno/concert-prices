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

def track_current_events():
    """
    Gets current prices for all tracked events.
    Also updates tracking to 0 for events that have passed.
    
    Returns:
        events_df: DataFrame with current prices (matches events table structure)
        event_details_tracking_df: DataFrame with event details (matches event_details table structure)
    """
    try:
        # 1. Set up database and API connections
        load_dotenv()
        api_key = os.getenv('CONSUMER_KEY')
        pg_user = os.getenv('POSTGRESQL_USER')
        pg_password = os.getenv('POSTGRESQL_PASSWORD')

        # 2. Create database connection (using psycopg2 directly)
        conn = psycopg2.connect(
            host=os.getenv('POSTGRESQL_HOST'),
            database="ticket_trail_db",
            user=os.getenv('POSTGRESQL_USER'),
            password=os.getenv('POSTGRESQL_PASSWORD')
        )

        # 3. Get all events that we're tracking
        query = """
            SELECT *
            FROM event_details
            WHERE tracking = 1
        """
        event_details_tracking_df = pd.read_sql(query, con=conn)

        if event_details_tracking_df.empty:
            print("No events are currently being tracked")
            return None, None

        # 4. Update tracking status and last_tracked date
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_date_dt = datetime.strptime(current_date, '%Y-%m-%d').date()
        
        # Update tracking status based on event date
        event_details_tracking_df['last_tracked'] = current_date
        event_details_tracking_df['tracking'] = event_details_tracking_df.apply(
            lambda row: 0 if pd.to_datetime(row['event_start_date']).date() <= current_date_dt else 1, 
            axis=1
        )

        # 5. Get current prices (rest of your existing code)
        events_data = []
        for _, row in event_details_tracking_df.iterrows():
            event_id = row['event_id']
            
            # Skip if we just marked this event as not tracking
            if row['tracking'] == 0:
                print(f"Event {event_id} has passed and will no longer be tracked")
                continue
                
            try:
                url = f"https://app.ticketmaster.com/discovery/v2/events/{event_id}.json"
                response = requests.get(
                    url, 
                    params={'apikey': api_key}, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    min_price = data['priceRanges'][0]['min']
                    
                    events_data.append({
                        'id': event_id,
                        'min_ticket_price': min_price,
                        'date_scraped': current_date
                    })
                    print(f"Updated price for event {event_id}: ${min_price}")
                else:
                    print(f"Failed to get data for event {event_id}")
                    
            except Exception as e:
                print(f"Error processing event {event_id}: {str(e)}")
                continue

        # 6. Create events DataFrame
        if events_data:
            events_df = pd.DataFrame(events_data)
        else:
            print("No price updates were successful")
            return None, None

        # 7. Update database with new tracking status
        cursor = conn.cursor()
        for _, row in event_details_tracking_df.iterrows():
            cursor.execute("""
                UPDATE event_details 
                SET tracking = %s, last_tracked = %s
                WHERE event_id = %s
            """, (row['tracking'], current_date, row['event_id']))
        
        # 8. Commit changes and close connections
        conn.commit()
        cursor.close()
        conn.close()

        return events_df, event_details_tracking_df

    except Exception as e:
        print(f"Error in track_current_events: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return None, None
  
