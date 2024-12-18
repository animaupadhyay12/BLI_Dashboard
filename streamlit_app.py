import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# File paths
DATA_FILE = "bls_data.csv"
DATE_TRACKER_FILE = "last_fetch_date.json"

# App title and description
st.title("BLS Monthly Data Dashboard")
st.write("This dashboard displays the latest Bureau of Labor Statistics (BLS) data trends.")

# Display last fetch date
if os.path.exists(DATE_TRACKER_FILE):
    with open(DATE_TRACKER_FILE, "r") as file:
        last_fetch_date = json.load(file).get("last_fetch", "Unknown")
        st.subheader(f"Last Data Update: {last_fetch_date}")
else:
    st.warning("No fetch date found. Data might be outdated.")

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
        fig, ax = plt.subplots()
        ax.plot(series_data['Date'], series_data['Value'], marker='o', linestyle='-')
        ax.set_title(f"Trend for {series_name}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.grid(True)

        # Display the plot
        st.pyplot(fig)
else:
    st.error("No data file found. Run the data fetch script first.")
