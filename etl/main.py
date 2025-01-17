from extract import search_event, track_current_events
from transform import transform
from load import load_to_sql
from dotenv import load_dotenv
import os

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('CONSUMER_KEY')
    pg_user = os.getenv('POSTGRESQL_USER')
    pg_password = os.getenv('POSTGRESQL_PASSWORD')

    try:
        # Step 1: Extract - Search for Sabrina Carpenter concert
        print("\n=== Initial Search and Load ===")
        print("\n--- Extracting Data ---")
        events_df, event_details_df, venues_df = search_event(
            key=api_key,
            keyword="Sabrina Carpenter",
            city=None
        )

        if events_df is None:
            print("No events found!")
            return

        print(f"Found event: {event_details_df['name'].iloc[0]}")

        # Step 2: Transform
        print("\n--- Transforming Data ---")
        events_df, event_details_df, venues_df = transform(events_df, event_details_df, venues_df)

        # Step 3: Load
        print("\n--- Loading Data ---")
        load_to_sql(
            pg_user=pg_user,
            pg_password=pg_password,
            events=events_df,
            event_details=event_details_df,
            venues=venues_df
        )

        # Print initial details
        print("\nInitial Event Details:")
        print(f"Artist: {event_details_df['name'].iloc[0]}")
        print(f"Genre: {event_details_df['genre'].iloc[0]}")
        print(f"Event Date: {event_details_df['event_start_date'].iloc[0]}")
        print(f"Initial Price: ${events_df['min_ticket_price'].iloc[0]}")
        print(f"Venue: {venues_df['venue_name'].iloc[0]}, {venues_df['city'].iloc[0]}, {venues_df['state'].iloc[0]}")

        # Step 4: Track Prices and Load Updates
        print("\n=== Testing Price Tracking ===")
        print("Checking tracked events...")
        
        tracked_events_df, tracked_details_df = track_current_events()
        
        if tracked_events_df is not None and not tracked_details_df.empty:
            # Load both price updates and tracking status updates
            print("\n--- Loading Updates ---")
            load_to_sql(
                pg_user=pg_user,
                pg_password=pg_password,
                events=tracked_events_df,        # New prices
                event_details=tracked_details_df, # Updated tracking status
                venues=None                      # No venue updates needed
            )
        else:
            print("\nNo events were tracked. This might mean:")
            print("1. No events are marked for tracking in the database")
            print("2. All tracked events have passed")
            print("3. There was an error getting the updated prices")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    main()