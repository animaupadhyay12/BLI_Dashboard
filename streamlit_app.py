import streamlit as st
import pandas as pd
import os
import json
from fetch_bls_data import fetch_bls_data  # Import the data fetching function

# File paths
DATA_FILE = "bls_data.csv"
DATE_TRACKER_FILE = "last_fetch_date.json"

def check_and_update_data():
    """Fetch new data at the beginning of the month if not already updated."""
    today = datetime.datetime.now()

    # Check if the fetch date file exists and read the last fetch date
    if os.path.exists(DATE_TRACKER_FILE):
        with open(DATE_TRACKER_FILE, "r") as file:
            last_fetch_date = json.load(file).get("last_fetch", None)
    else:
        last_fetch_date = None

    # Determine if a new fetch is needed (first day of the month or missing data)
    if last_fetch_date is None or today.strftime("%Y-%m") > last_fetch_date[:7]:
        st.info("Fetching new data for the beginning of the month...")
        fetch_bls_data()
        st.success("Data updated successfully!")
    else:
        st.success(f"Data is already up-to-date. Last updated: {last_fetch_date}")

# App title
st.title("BLS Monthly Data Dashboard")
st.write("This dashboard displays the latest Bureau of Labor Statistics (BLS) data trends.")

check_and_update_data()

# Display the last fetch date
if os.path.exists(DATE_TRACKER_FILE):
    with open(DATE_TRACKER_FILE, "r") as file:
        last_fetch_date = json.load(file).get("last_fetch", "No date available")
        st.subheader(f"Last Data Update: {last_fetch_date}")
else:
    st.warning("No fetch date found. Please fetch new data.")

# Load and display data
if os.path.exists(DATA_FILE):
    data = pd.read_csv(DATA_FILE)

    # Display data table
    st.subheader("Data Table")
    st.write(data)

    # Visualizations
    st.subheader("Data Visualization")
    series_names = data['Series Name'].unique()

    for series_name in series_names:
        st.write(f"### {series_name}")
        series_data = data[data['Series Name'] == series_name].copy()
        series_data['Date'] = pd.to_datetime(series_data[['Year', 'Month']].assign(day=1))
        series_data = series_data.sort_values('Date')

        # Plot the data
        st.line_chart(series_data.set_index("Date")['Value'])
else:
    st.error("No data file found. Click 'Fetch New Data' to generate it.")
