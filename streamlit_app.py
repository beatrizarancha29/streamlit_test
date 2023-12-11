import streamlit as st
from PIL import Image
import pandas as pd
import requests
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Function to get real-time electricity prices from the external API
def get_electricity_prices():
    endpoint = 'https://apidatos.ree.es'
    get_archives = '/es/datos/mercados/precios-mercados-tiempo-real'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Host': 'apidatos.ree.es'}

    now = datetime.datetime.now()
    start_date = now.strftime('%Y-%m-%dT%H:%M')
    end_date = (now + datetime.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M')

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

# Fetch weather data for the entire month
city_name = "New York"  # You can make it dynamic based on user input
weather_data = get_weather_data(city_name)

# Extract temperature and date data from the API response
temperatures = [day['day'].get('avgtemp_c') for day in weather_data if 'day' in day and 'avgtemp_c' in day['day']]
dates = [day['date'] for day in weather_data if 'date' in day]

# Update the Temperature metric to display the entire month's forecast
if temperatures:
    b1.metric("Temperature", f"Min: {min(temperatures):.2f} °C, Max: {max(temperatures):.2f} °C", "-")
else:
    b1.warning("Temperature data not available")

# Continue with existing metrics
b2.metric("Electricity Price", f"{round(min(0.10, 0.50), 2)} - {round(max(0.10, 0.50), 2)} $/kWh", "-")
b3.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed
b4.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed

# Row C
c1, c2 = st.columns((7, 3))
with c1:
    st.markdown('### Temperature Trend')
    if temperatures:
        st.line_chart(pd.DataFrame({'Temperature': temperatures}, index=dates))
    else:
        st.warning("Temperature data not available")
with c2:
    st.markdown('### Electricity Price Trend')
    
    # Get real-time electricity prices
    real_time_prices, real_time_times = get_electricity_prices()

    if real_time_prices:
        # Plot the real-time electricity prices
        plt.plot(real_time_times, real_time_prices, label='Real-time Prices', marker='o')
        plt.xlabel('Time')
        plt.ylabel('Electricity Price ($/kWh)')
        plt.title('Real-time Electricity Price Variation')
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt)
    else:
        st.warning("Real-time electricity price data not available")

# Row D
d1, d2 = st.columns((7, 3))
with d1:
    st.markdown('### Statistics')
    # Replace this with any statistics or summary you want to display
    if temperatures:
        st.text(f"Average Temperature: {round(np.mean(temperatures), 2)} °C")
        st.text(f"Average Electricity Price: {round(np.mean(real_time_prices), 2)} $/kWh")
    else:
        st.warning("Statistics not available")
with d2:
    pass  # Removed the content of the second column (previously combined trend)
