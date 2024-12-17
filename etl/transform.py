import pandas as pd

def transform(events, event_details, venues_list):
    """
    Does the following data transformations
    1. Cleans the dates for event_start_date, public_sales_start, public_sales_end, presale_start, presale_end

    User inputs the 3 uncleaned dataframes: events, event_details, venues_list
    Outputs the cleaned dataframes
    """
    # Clean dates in the event_details table
    event_details['event_start_date'] = pd.to_datetime(event_details['event_start_date']).dt.date
    event_details['public_sales_start'] = pd.to_datetime(event_details['public_sales_start']).dt.date
    event_details['public_sales_end'] = pd.to_datetime(event_details['public_sales_end']).dt.date
    event_details['presale_start'] = pd.to_datetime(event_details['presale_start']).dt.date
    event_details['presale_end'] = pd.to_datetime(event_details['presale_end']).dt.date

    return events, event_details, venues_list
