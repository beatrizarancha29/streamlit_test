import streamlit as st
from PIL import Image
import pandas as pd
import requests
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Function to get weather data from the external API
def get_weather_data(city, days=7):
    api_key = '46b2788544324cc8ada143152230512'  # Replace with your actual weather API key
    response = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days={days}')
    
    try:
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()['forecast']['forecastday']
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting weather data: {e}")
        return []

# Function to get real-time electricity prices from the external API with hourly increments
def get_electricity_prices():
    endpoint = 'https://apidatos.ree.es'
    get_archives = '/es/datos/mercados/precios-mercados-tiempo-real'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Host': 'apidatos.ree.es'}

    now = datetime.datetime.now()
    start_date = now.strftime('%Y-%m-%dT%H:%M')
    end_date = (now + datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')  # 24 hours from now

    params = {'start_date': start_date, 'end_date': end_date, 'time_trunc': 'hour'}

    try:
        response = requests.get(endpoint + get_archives, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if 'included' in data:
            prices = [item['attributes']['values'][0]['value'] for item in data['included']]
            times = [item['attributes']['values'][0]['datetime'] for item in data['included']]
            return prices, times
        else:
            st.warning("Electricity price data not available")
            return [], []

    except requests.exceptions.RequestException as e:
        st.error(f"Error making API request: {e}")
        return [], []

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

# Fetch weather data for the entire week
city_name = "Barcelona"  # Barcelona, Spain
weather_data_week = get_weather_data(city_name, days=7)

# Extract temperature and date data from the API response for the week
temperatures_week = [day['day'].get('avgtemp_c') for day in weather_data_week if 'day' in day and 'avgtemp_c' in day['day']]
dates_week = [datetime.datetime.strptime(day['date'], '%Y-%m-%d') for day in weather_data_week if 'date' in day]

# Update the Temperature metric to display the entire week's forecast
if temperatures_week:
    b1.bar_chart(pd.DataFrame({'Temperature': temperatures_week}, index=dates_week))
else:
    b1.warning("Temperature data not available for the week")

# Fetch weather data for the entire day
weather_data_day = get_weather_data(city_name, days=1)

# Extract temperature and date data from the API response for the day
try:
    temperatures_day = [hour['hour'].get('temp_c') for hour in weather_data_day[0]['hour']]
    hours_day = [datetime.datetime.strptime(hour['time'], '%Y-%m-%d %H:%M') for hour in weather_data_day[0]['hour']]
except (KeyError, TypeError):
    st.warning("Temperature data not available for the day")
    temperatures_day = []
    hours_day = []

# Update the Temperature metric to display the entire day's forecast
if temperatures_day:
    b2.bar_chart(pd.DataFrame({'Temperature': temperatures_day}, index=hours_day))
else:
    b2.warning("Temperature data not available for the day")

# Continue with existing metrics
real_time_prices, _ = get_electricity_prices()
if real_time_prices:
    b3.metric("Electricity Price", f"{round(min(real_time_prices), 2)} - {round(max(real_time_prices), 2)} $/kWh", "-")
else:
    b3.warning("Electricity price data not available for the day")

# ... (Remaining code)

# Row D
d1, d2 = st.columns((7, 3))
with d1:
    st.markdown('### Statistics')
    # Replace this with any statistics or summary you want to display
    if temperatures_week and real_time_prices:
        st.text(f"Weekly Average Temperature: {round(np.mean(temperatures_week), 2)} °C")
        st.text(f"Weekly Average Electricity Price: {round(np.mean(real_time_prices), 2)} $/kWh")
    else:
        st.warning("Statistics not available for the week")
with d2:
    pass  # Removed the content of the second column (previously combined trend)
