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
        return None
    
    # Extract info for events
    events = []
    event_details = []
    for event in data['_embedded']['events']:
        # Pulling data for events table
        event_id = event.get('id', None)
        artist = event['_embedded']['attractions'][0]['name']
        #ticket_price = pass
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
        # Put all results in a dictionary
        event_dict = {
            'id' : event_id,
            'artist' : artist,
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
            'presale_end' : presale_end
        }


        # Add to list
        events.append(event_dict)
        event_details.append(event_details_dict)


    return events, event_details


# Load in API keys
load_dotenv()

api_key = os.getenv('CONSUMER_KEY')

event_list, event_details_list = search_event(keyword = 'Tyler The Creator', key = api_key)
print(event_list)
print(event_details_list)