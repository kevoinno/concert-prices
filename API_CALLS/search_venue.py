from dotenv import load_dotenv
import os
import requests
import json

def extract_venue_data(api_response):
    """
        Takes in a reponse from an a venue_search call and extracts the name and id of the venue
    """
    try:
        venues_data = []
        
        # Check if '_embedded' and 'venues' keys exist in the response
        if "_embedded" in api_response and "venues" in api_response["_embedded"]:
            venues = api_response["_embedded"]["venues"]
            
            # Loop through each venue and extract relevant fields
            for venue in venues:
                venue_name = venue.get("name", "Unknown Name")
                venue_id = venue.get("id", "Unknown ID")
                venues_data.append({"name": venue_name, "id": venue_id})
        else:
            print("No venues found in the response.")

        return venues_data
    except Exception as e:
        print("Error extracting venue data:", e)
        return []

# Load in API keys
load_dotenv()

api_key = os.getenv('CONSUMER_KEY')
api_url_venue_search = "https://app.ticketmaster.com/discovery/v2/venues.json"

# Specify params
venue_search = 'Crypto Arena'

params = {
    "apikey" : api_key,
    "keyword" : venue_search,
    "countryCode" : "US"
}

#Get response TO SEARCH EVENT
response = requests.get(api_url_venue_search, params = params)

try:
    if response.status_code == 200:
        data = response.json()

        venues = extract_venue_data(data)
        print(venues)
except Exception as e:
    print('Failed to get data: ', e)




#   Get response TO GET EVENT DETAILS
# response = requests.get(api_url_venue_details, params=params)

# # Process the response
# try:
#     if response.status_code == 200:
#         # Parse the JSON response
#         data = response.json()

#         # Extract specific venue details
#         venue_name = data.get("name", "Unknown Venue")
#         city = data.get("city", {}).get("name", "Unknown City")
#         state = data.get("state", {}).get("stateCode", "Unknown State")

#         # Print the extracted details
#         print(f"Venue Name: {venue_name}")
#         print(f"City: {city}")
#         print(f"State: {state}")

#     else:
#         print(f"Failed to fetch venue details. Status code: {response.status_code}")
# except Exception as e:
#     print("An error occurred:", e)



