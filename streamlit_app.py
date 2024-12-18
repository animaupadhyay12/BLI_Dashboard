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

# Button to fetch the latest data
if st.button("Fetch Latest Data"):
    from fetch_bls_data import fetch_bls_data  # Import the function
    fetch_bls_data()  # Call the function to fetch new data
    st.success("Data updated! Refresh the page to see the changes.")

# Display last fetch date
if os.path.exists(DATE_TRACKER_FILE):
    with open(DATE_TRACKER_FILE, "r") as file:
        last_fetch_date = json.load(file).get("last_fetch", "Unknown")
        st.subheader(f"Last Data Update: {last_fetch_date}")
else:
    st.warning("No last fetch date found. Please run the data fetch script.")

# Check if data file exists
if os.path.exists(DATA_FILE):
    # Load the data
    data = pd.read_csv(DATA_FILE)
    
    # Display data table
    st.subheader("Data Table")
    st.write(data)

    # Data visualization
    st.subheader("Data Visualization")
    series_ids = data['Series ID'].unique()
    
    for series_id in series_ids:
        # Create a subset of data for the current series
        series_data = data[data['Series ID'] == series_id].copy()
        series_data['Date'] = pd.to_datetime(series_data[['Year', 'Month']].assign(day=1))
        series_data = series_data.sort_values('Date')
        
        # Plot the data
        fig, ax = plt.subplots()
        ax.plot(series_data['Date'], series_data['Value'], marker='o', linestyle='-')
        ax.set_title(f"Trend for Series: {series_id}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.grid(True)
        
        # Show the plot in Streamlit
        st.pyplot(fig)
else:
    st.error("Data file not found. Please run the data fetch script to generate 'bls_data.csv'.")
