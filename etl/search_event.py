from dotenv import load_dotenv
import os
import requests
import json

# Load in API keys
load_dotenv()

api_key = os.getenv('CONSUMER_KEY')
api_url_events_search = 'https://app.ticketmaster.com/discovery/v2/events.json'

# Specify params
keyword = 'Tyler The Creator'
params = {
    "apikey" : api_key,
    "keyword" : keyword,
    "countryCode" : "US",
    "size" : 5
}

# Make the GET request
response = requests.get(api_url_events_search, params=params)

# Process the response
try:
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Check if events are returned in the response
        if "_embedded" in data and "events" in data["_embedded"]:
            events = data["_embedded"]["events"]

            # Loop through each event and display details
            print("Events Found:")
            for event in events:
                event_name = event.get("name", "Unknown Event Name")
                event_date = event["dates"]["start"].get("localDate", "Unknown Date")
                venue_name = event["_embedded"]["venues"][0].get("name", "Unknown Venue")
                city = event["_embedded"]["venues"][0]["city"].get("name", "Unknown City")
                state = event["_embedded"]["venues"][0]["state"].get("stateCode", "Unknown State")

                print(f"Event Name: {event_name}")
                print(f"Date: {event_date}")
                print(f"Venue: {venue_name}")
                print(f"City: {city}, {state}")
                print("-" * 30)
        else:
            print("No events found for the given keyword.")
    else:
        print(f"API call failed with status code: {response.status_code}")
except Exception as e:
    print("An error occurred:", e)


