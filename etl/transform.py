import pandas as pd
import numpy as np

def transform(events, event_details, venues_list):
    """
    Transform event data with basic validation
    """
    try:
        if event_details is not None:
            # Convert dates safely
            date_columns = ['event_start_date', 'public_sales_start', 
                          'public_sales_end', 'presale_start', 'presale_end']
            
            for col in date_columns:
                event_details[col] = pd.to_datetime(event_details[col]).dt.date
            
            # Replace NaN with None
            event_details = event_details.replace({pd.NaT: None})
            
        return events, event_details, venues_list
        
    except Exception as e:
        print(f"Error in transform function: {str(e)}")
        return None, None, None
