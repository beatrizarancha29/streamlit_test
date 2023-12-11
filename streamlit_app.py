import streamlit as st
from PIL import Image
import pandas as pd
import requests
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Function to get weather data from the OpenWeatherMap API
def get_weather_data(api_key, city):
    endpoint = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {'q': city, 'appid': api_key}

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()['list']
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting weather data: {e}")
        return []

# Function to get real-time electricity prices (simulated data)
def get_electricity_prices():
    now = datetime.datetime.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + datetime.timedelta(hours=23, minutes=59)

    times = pd.date_range(start=start_time, end=end_time, freq='H')
    prices = np.random.uniform(0.1, 0.5, len(times))

    return prices, times

# Page setting
st.set_page_config(layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Here starts the web app design
# Row A
a1, a2, a3 = st.columns(3)
a1.image(Image.open('autoprice.png'))
a2.metric("Wind", "-", "-")  # Replace with actual data or remove if not needed
a3.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed

# Row B
b1, b2, b3, b4 = st.columns(4)

# Fetch weather data for the next 7 days using OpenWeatherMap API
city_name = "Barcelona"
openweathermap_api_key = "84e73656e11445cd7ddcc77a98850373"  # Replace with your actual API key
weather_data_week = get_weather_data(openweathermap_api_key, city_name)

# Extract temperature and date data from the API response for the week
temperatures_week = [item['main']['temp'] for item in weather_data_week]
dates_week = [datetime.datetime.fromtimestamp(item['dt']) for item in weather_data_week]

# Update the Temperature metric to display the entire week's forecast
if temperatures_week:
    b1.bar_chart(pd.DataFrame({'Temperature': temperatures_week}, index=dates_week))
else:
    b1.warning("Temperature data not available for the week")

# Fetch electricity prices for the next 24 hours (simulated data)
real_time_prices, real_time_times = get_electricity_prices()

# Update the Temperature metric to display the entire day's forecast
if real_time_prices.any():
    b2.line_chart(pd.DataFrame({'Electricity Price': real_time_prices}, index=real_time_times))
else:
    b2.warning("Electricity price data not available for the day")

# Continue with existing metrics
b3.metric("Electricity Price", f"{round(min(0.10, 0.50), 2)} - {round(max(0.10, 0.50), 2)} $/kWh", "-")
b4.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed

# Row C
c1, c2 = st.columns((7, 3))
with c1:
    st.markdown('### Temperature Trend for the Week')
    if temperatures_week:
        st.line_chart(pd.DataFrame({'Temperature': temperatures_week}, index=dates_week))
    else:
        st.warning("Temperature data not available for the week")
with c2:
    st.markdown('### Electricity Price Trend for the Day')

# Row D
d1, d2 = st.columns((7, 3))
with d1:
    st.markdown('### Statistics')
    # Replace this with any statistics or summary you want to display
    if temperatures_week:
        st.text(f"Weekly Average Temperature: {round(np.mean(temperatures_week), 2)} °C")
        st.text(f"Weekly Average Electricity Price: {round(np.mean(real_time_prices), 2)} $/kWh")
    else:
        st.warning("Statistics not available for the week")
with d2:
    pass  # Removed the content of the second column (previously combined trend)
