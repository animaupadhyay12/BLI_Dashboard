import requests
import json
import pandas as pd
import datetime
import os

DATE_TRACKER_FILE = "last_fetch_date.json"
DATA_FILE = "bls_data.csv"

SERIES_NAME_MAP = {
    "LNS14000000": "Unemployment Rate (16+ years)",
    "CES0000000001": "Total Nonfarm Employment",
    "LNS11000000": "Civilian Labor Force Level",
    "LNS12000000": "Civilian Employment Level",
    "LNS13000000": "Civilian Unemployment Level",
    "CES0500000002": "Average Weekly Hours - Total Private",
    "CES0500000007": "Average Hourly Earnings - Total Private"
}

def update_fetch_date():
    with open(DATE_TRACKER_FILE, "w") as file:
        json.dump({"last_fetch": datetime.datetime.now().strftime("%Y-%m-%d")}, file)

def fetch_bls_data():
    headers = {'Content-type': 'application/json'}
    current_year = datetime.datetime.now().year
    payload = json.dumps({
        "seriesid": list(SERIES_NAME_MAP.keys()),
        "startyear": str(current_year - 1),
        "endyear": str(current_year)
    })

    try:
        response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=payload, headers=headers)
        response.raise_for_status()
        json_data = response.json()

        all_series_data = []
        for series in json_data.get('Results', {}).get('series', []):
            series_id = series['seriesID']
            series_name = SERIES_NAME_MAP.get(series_id, series_id)
            for item in series['data']:
                if 'M01' <= item['period'] <= 'M12':  # Monthly data only
                    all_series_data.append({
                        "Series Name": series_name,
                        "Year": int(item['year']),
                        "Month": int(item['period'][1:]),
                        "Value": float(item['value'])
                    })

        if all_series_data:
            df_new = pd.DataFrame(all_series_data)

            if os.path.exists(DATA_FILE):
                df_existing = pd.read_csv(DATA_FILE)
                df_combined = pd.concat([df_existing, df_new]).drop_duplicates()
            else:
                df_combined = df_new

            df_combined.to_csv(DATA_FILE, index=False)
            update_fetch_date()
            print("Data successfully fetched and appended.")
        else:
            print("No data was returned.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_bls_data()
