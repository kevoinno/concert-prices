import psycopg2
import os
from dotenv import load_dotenv

def test_connection():
    # Load environment variables
    print("Starting test...")
    loaded = load_dotenv()
    print(f"Environment loaded: {loaded}")
    
    # Print ALL environment variables (except password)
    print("\nEnvironment variables:")
    for key in ['POSTGRESQL_HOST', 'POSTGRESQL_USER']:
        value = os.getenv(key)
        print(f"{key}: {value if value else 'NOT FOUND'}")
    
    # Try database connection
    print("\nTesting database connection...")
    try:
        print("Attempting to connect...")
        conn = psycopg2.connect(
            host=os.getenv('POSTGRESQL_HOST'),
            database="ticket_trail_db",
            user=os.getenv('POSTGRESQL_USER'),
            password=os.getenv('POSTGRESQL_PASSWORD')
        )
        print("Connection successful!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nDebug info:")
        print(f"Host type: {type(os.getenv('POSTGRESQL_HOST'))}")
        print(f"Host value: {os.getenv('POSTGRESQL_HOST')}")

if __name__ == "__main__":
    test_connection() 