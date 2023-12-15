import streamlit as st
import time
from PIL import Image
import pandas as pd
import requests
import numpy as np
import datetime
import matplotlib.pyplot as plt
import webbrowser

# Function to get weather data from the external API
def get_weather_data(city):
    api_key = '46b2788544324cc8ada143152230512'  # Replace with your actual weather API key
    response = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=30')
    return response.json()['forecast']['forecastday']

# Function to get the electricity prices for a specific day and hour
def get_electricity_price_for_date(date, hour):
    # Actual values for endpoint, get_archives, and headers
    endpoint = 'https://apidatos.ree.es'
    get_archives = '/es/datos/mercados/precios-mercados-tiempo-real'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Host': 'apidatos.ree.es'
    }

    start_date = f'{date}T{hour}:00'
    end_date = f'{date}T{hour}:59'
    params = {'start_date': start_date, 'end_date': end_date, 'time_trunc': 'hour'}

    try:
        response = requests.get(endpoint + get_archives, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Check if 'included' key is present in the response
        if 'included' in data:
            # Find the 'values' field under 'attributes'
            for item in data['included']:
                if 'values' in item['attributes']:
                    # Assuming the API response contains a 'values' field with a 'value' for the electricity price
                    price = item['attributes']['values'][0]['value']
                    # Convert price from €/MWh to €/kWh
                    price_per_kwh = price / 1000
                    return price_per_kwh

            print(f"Error: 'values' key not found in 'attributes'. Response: {data}")
            return None
        else:
            print(f"Error: 'included' key not found in response. Response: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

# Function to get data from the provided link
@st.cache(ttl=300)  # Cache for 5 minutes
def get_sensor_data():
    data_url = 'https://raw.githubusercontent.com/AbdullahUPC/ControlProject/main/hello.txt'
    response = requests.get(data_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching sensor data. Status Code: {response.status_code}")
        return None

# Page setting
st.set_page_config(layout="wide")

# Here starts the web app design
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Row A
a1, a2, a3 = st.columns(3)
a1.image(Image.open('autoprice.png'))

# Row B
b1, b2, b3, b4 = st.columns(4)

# Row C
c1, c2 = st.columns((7, 3))

# Row D
d1, d2, d3 = st.columns((5, 5, 2))

# Button to call the price API
fetch_button_pressed = st.button("Fetch Electricity Prices")

# Button to access the Receiver Statistics page
if st.button("Receiver Statistics"):
    webbrowser.open_new_tab("http://www.xyz.com")

# Initial empty placeholders
sensor_placeholder = st.empty()
temperature_chart_placeholder = st.empty()
electricity_price_chart_placeholder = st.empty()

# Loop for dynamic updating
while True:
   
    # Fetch and display sensor data
    sensor_data = get_sensor_data()
    if sensor_data:
        lines = sensor_data.split(', ')
        for line in lines:
            if "Temperature 1" in line:
                temp_sensor1 = line.split(': ')[1].replace('°K', '°C')
                sensor_placeholder.metric("Temperature Sensor 1", temp_sensor1, "-")
            elif "Temperature 2" in line:
                temp_sensor2 = line.split(': ')[1].replace('°K', '°C')
                sensor_placeholder.metric("Temperature Sensor 2", temp_sensor2, "-")
            elif "LED Status" in line:
                led_status = line.split(': ')[1]
                sensor_placeholder.metric("LED Status", led_status, "-")

    # Fetch and display electricity prices
    if fetch_button_pressed:
        prices = []
        hours_of_day = range(24)
        for hour in hours_of_day:
            price = get_electricity_price_for_date(previous_day, hour)
            print(f"The electricity price for {previous_day} {hour} is {price} €/kWh at {hour}:00.")
            prices.append(price)

        # Display electricity price chart
        electricity_price_chart_placeholder.line_chart(pd.DataFrame({'Electricity Price': prices}, index=hours_of_day))

    # Fetch and display temperature chart
    city_name = "Barcelona"  # Dynamically set to Barcelona
    weather_data = get_weather_data(city_name)
    temperatures = [day['day'].get('avgtemp_c') for day in weather_data if 'day' in day and 'avgtemp_c' in day['day']]
    dates = [day['date'] for day in weather_data if 'date' in day]
    if temperatures:
        temperature_chart_placeholder.line_chart(pd.DataFrame({'Temperature': temperatures}, index=dates))
    else:
        temperature_chart_placeholder.warning("Temperature data not available")
