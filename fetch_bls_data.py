import requests
import json
import pandas as pd
import datetime
import os

# File paths
DATE_TRACKER_FILE = "last_fetch_date.json"  # Tracks the last fetch date
DATA_FILE = "bls_data.csv"                 # File where data is saved

def should_update_data():
    """Check if data should be updated based on the last fetch date."""
    if not os.path.exists(DATE_TRACKER_FILE):
        return True
    with open(DATE_TRACKER_FILE, "r") as file:
        data = json.load(file)
        last_fetch_date = datetime.datetime.strptime(data["last_fetch"], "%Y-%m-%d")
    return (datetime.datetime.now() - last_fetch_date).days >= 30

def update_fetch_date():
    """Update the last fetch date to today."""
    with open(DATE_TRACKER_FILE, "w") as file:
        json.dump({"last_fetch": datetime.datetime.now().strftime("%Y-%m-%d")}, file)

def fetch_bls_data():
    """Fetch data from the BLS API."""
    headers = {'Content-type': 'application/json'}
    current_year = datetime.datetime.now().year
    last_year = current_year - 1
    payload = json.dumps({
        "seriesid": [
            "LNS14000000",  # Unemployment rate
            "CES0000000001",  # Total nonfarm employment
            "LNS11000000",  # Civilian labor force level
            "LNS12000000",  # Civilian employment level
            "LNS13000000",  # Civilian unemployment level
            "CES0500000002",  # Total private average weekly hours
            "CES0500000007"  # Total private average hourly earnings
        ],
        "startyear": str(last_year),
        "endyear": str(current_year)
    })

    # Make the API request
    response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=payload, headers=headers)
    json_data = response.json()

    # Check for errors
    if "message" in json_data and "REQUEST_NOT_PROCESSED" in json_data.get("status", ""):
        print(f"Error: {json_data['message'][0]}")
        return

    # Parse the data
    all_series_data = []
    for series in json_data.get('Results', {}).get('series', []):
        series_id = series['seriesID']
        for item in series['data']:
            # Include only monthly data (M01-M12)
            if 'M01' <= item['period'] <= 'M12':
                all_series_data.append({
                    "Series ID": series_id,
                    "Year": int(item['year']),
                    "Month": int(item['period'][1:]),
                    "Value": float(item['value'])
                })

    # Save the data to a CSV file
    if all_series_data:
        df = pd.DataFrame(all_series_data)
        df.to_csv(DATA_FILE, index=False)
        update_fetch_date()
        print(f"Data successfully fetched and saved to {DATA_FILE}.")
    else:
        print("No data returned. Check the API response for details.")

if __name__ == "__main__":
    # Fetch data if the file doesn't exist or the data is outdated
    if not os.path.exists(DATA_FILE) or should_update_data():
        print("Fetching updated data...")
        fetch_bls_data()
    else:
        print("Data is already up to date. No fetch required.")
