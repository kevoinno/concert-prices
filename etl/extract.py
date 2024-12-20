import pandas as pd
from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime

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

        events_df = pd.DataFrame(events)
        events_details_df = pd.DataFrame(event_details)
        venues_df = pd.DataFrame(venues)
    return events_df, events_details_df, venues_df
