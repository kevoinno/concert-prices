from dotenv import load_dotenv
import os
import requests
import json

# Load in API keys
load_dotenv()

api_key = os.getenv('CONSUMER_KEY')
api_url_venue_search = "https://app.ticketmaster.com/discovery/v2/venues.json"
venue_id = 'KovZpZAEdntA'
api_url_venue_details =  f"https://app.ticketmaster.com/discovery/v2/venues/{venue_id}.json"

# Specify params
params = {
    "apikey" : api_key,
    "countryCode" : "US"
}

#Get response TO GET EVENT DETAILS
response = requests.get(api_url_venue_details, params=params)

# Process the response
try:
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract specific venue details
        venue_name = data.get("name", "Unknown Venue")
        city = data.get("city", {}).get("name", "Unknown City")
        state = data.get("state", {}).get("stateCode", "Unknown State")

        # Print the extracted details
        print(f"Venue Name: {venue_name}")
        print(f"City: {city}")
        print(f"State: {state}")

    else:
        print(f"Failed to fetch venue details. Status code: {response.status_code}")
except Exception as e:
    print("An error occurred:", e)



