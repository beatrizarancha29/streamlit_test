import streamlit as st
from PIL import Image
import pandas as pd
import requests
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
        response.raise_for_status()
        data = response.json()

        for item in data.get('included', []):
            if 'values' in item.get('attributes', {}):
                price = item['attributes']['values'][0]['value']
                return price / 1000

        print(f"Error: Price data not found in the response. Response: {data}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

# Function to get sensor data with a timestamp to force cache invalidation
def get_sensor_data():
    timestamp = datetime.datetime.now().timestamp()
    data_url = f'https://raw.githubusercontent.com/AbdullahUPC/ControlProject/main/hello.txt?timestamp={timestamp}'
    response = requests.get(data_url)
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching sensor data. Status Code: {response.status_code}")
        return None

# Function to display temperature metrics
def display_temperature_metrics(sensor_data):
    lines = sensor_data.split(', ')
    for line in lines:
        if "Temperature 1" in line:
            temp_sensor1 = line.split(': ')[1].replace('°K', '°C')
            st.metric("Temperature Sensor 1", temp_sensor1, "-")
        elif "Temperature 2" in line:
            temp_sensor2 = line.split(': ')[1].replace('°K', '°C')
            st.metric("Temperature Sensor 2", temp_sensor2, "-")
        elif "LED Status" in line:
            led_status = line.split(': ')[1]
            st.metric("LED Status", led_status, "-")

# Function to display weather metrics
def display_weather_metrics(temperatures):
    if temperatures:
        st.metric("Temperature", f"Min: {min(temperatures):.2f} °C, Max: {max(temperatures):.2f} °C", "-")
    else:
        st.warning("Temperature data not available")

# Function to display electricity and LED metrics
def display_electricity_and_led_metrics():
    st.metric("Electricity Price", f"{round(min(0.10, 0.50), 2)} - {round(max(0.10, 0.50), 2)} €/kWh", "-")
    st.metric("LED Status", "-", "-")

# Function to display temperature trend chart
def display_temperature_trend_chart(temperatures):
    st.markdown('### Temperature Trend')
    if temperatures:
        st.line_chart(pd.DataFrame({'Temperature': temperatures}))
    else:
        st.warning("Temperature data not available")

# Function to fetch and display electricity prices
def display_electricity_prices():
    # Fetch electricity prices for the previous day
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    previous_day = yesterday.strftime('%Y-%m-%d')
    hours_of_day = range(24)
    prices = []

    # Button to call the price API
    fetch_button_pressed = st.button("Fetch Electricity Prices")
    if fetch_button_pressed:
        for hour in hours_of_day:
            price = get_electricity_price_for_date(previous_day, hour)
            print(f"The electricity price for {previous_day} {hour} is {price} €/kWh at {hour}:00.")
            prices.append(price)

    # Display Electricity Price Trend
    st.markdown('### Electricity Price Trend')
    if fetch_button_pressed:
        plt.plot(hours_of_day, prices, marker='o')
        plt.title(f'Electricity Prices on {previous_day}')
        plt.xlabel('Hour of the Day')
        plt.ylabel('Electricity Price (€/kWh)')
        st.pyplot(plt)
    else:
        st.warning("Please press the 'Fetch Electricity Prices' button.")

# Function to display statistics
def display_statistics(temperatures, prices):
    st.markdown('### Statistics')
    if temperatures and prices:
        st.text(f"Average Temperature: {round(np.mean(temperatures), 2)} °C")
        st.text(f"Average Electricity Price: {round(np.mean(prices), 2)} €/kWh")
    elif fetch_button_pressed:
        st.warning("Statistics not available")

# Function to open the Receiver Statistics page
def open_receiver_statistics_page():
    if st.button("Receiver Statistics"):
        webbrowser.open_new_tab("http://www.xyz.com")

# Page setting
st.set_page_config(layout="wide")

# Counter initialization
if 'count' not in st.session_state:
    st.session_state.count = 1  # or 0 depending on your initial condition

# Row A
a1, a2, a3 = st.columns(3)
a1.image(Image.open('autoprice.png'))

# Check the counter value to determine which section to display
if st.session_state.count == 1:
    # Display Temperature Sensor 1, Temperature Sensor 2, and LED Status
    sensor_data = get_sensor_data()
    if sensor_data:
        display_temperature_metrics(sensor_data)
    st.session_state.count = 0
else:
    st.session_state.count = 1

# Row B
b1, b2, b3, b4 = st.columns(4)

# Fetch weather data for the entire month in Barcelona
city_name = "Barcelona"  # Dynamically set to Barcelona
weather_data = get_weather_data(city_name)

# Extract temperature and date data from the API response
temperatures = [day['day'].get('avgtemp_c') for day in weather_data if 'day' in day and 'avgtemp_c' in day['day']]
dates = [day['date'] for day in weather_data if 'date' in day]

# Update the Temperature metric to display the entire month's forecast
display_weather_metrics(temperatures)

# Continue with existing metrics
display_electricity_and_led_metrics()

# Row C
c1, c2 = st.columns((7, 3))
with c1:
    display_temperature_trend_chart(temperatures)

# Row D
d1, d2, d3 = st.columns((5, 5, 2))
with d1:
    display_electricity_prices()

with d2:
    display_statistics(temperatures, prices)

with d3:
    pass  # Removed the content of the second column (previously combined trend)

# Receiver Statistics Button
open_receiver_statistics_page()
