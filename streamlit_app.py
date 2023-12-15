import streamlit as st
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
def get_sensor_data():
    data_url = 'https://raw.githubusercontent.com/AbdullahUPC/ControlProject/main/hello.txt'
    response = requests.get(data_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching sensor data. Status Code: {response.status_code}")
        return None

# Function to update temperature sensor values
def update_temperature_values(a2, a3):
    sensor_data = get_sensor_data()
    if sensor_data:
        lines = sensor_data.split(', ')
        for line in lines:
            if "Temperature 1" in line:
                temp_sensor1 = line.split(': ')[1].replace('°K', '°C')
                a2.metric("Temperature Sensor 1", temp_sensor1, "-")
            elif "Temperature 2" in line:
                temp_sensor2 = line.split(': ')[1].replace('°K', '°C')
                a3.metric("Temperature Sensor 2", temp_sensor2, "-")
            elif "LED Status" in line:
                led_status = line.split(': ')[1]
                a2.metric("LED Status", led_status, "-")

# Page setting
st.set_page_config(layout="wide")

# Here starts the web app design
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Row A
a1, a2, a3 = st.columns(3)
a1.image(Image.open('autoprice.png'))

# Display Temperature Sensor 1, Temperature Sensor 2, and LED Status
update_temperature_values(a2, a3)

# Row B
b1, b2, b3, b4 = st.columns(4)

# ... (rest of your code remains unchanged)

# Button to update the temperature sensor values
update_button = st.button("Update Temperature Sensors")

# Button to access the Receiver Statistics page
if st.button("Receiver Statistics"):
    webbrowser.open_new_tab("http://www.xyz.com")

# Update temperature sensor values when the button is clicked
if update_button:
    update_temperature_values(a2, a3)
