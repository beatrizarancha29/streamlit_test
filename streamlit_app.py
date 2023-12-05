import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import requests

# Function to get weather data from the external API
def get_weather_data(city):
    api_key = '46b2788544324cc8ada143152230512'
    response = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=30')
    return response.json()['forecast']['forecastday']

# Dummy data for illustration (replace this with your actual data)
electricity_prices = np.random.uniform(0.10, 0.50, size=30)

# Page setting
st.set_page_config(layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Here starts the web app design
# Row A
a1, a2, a3 = st.columns(3)
a1.image(Image.open('streamlit-logo-secondary-colormark-darktext.png'))
a2.metric("Wind", "-", "-")  # Replace with actual data or remove if not needed
a3.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed

# Row B
b1, b2, b3, b4 = st.columns(4)

# Fetch weather data for the entire month
city_name = "New York"  # You can make it dynamic based on user input
weather_data = get_weather_data(city_name)
temperatures = [day['day']['avgtemp_c'] for day in weather_data]

# Update the Temperature metric to display the entire month's forecast
b1.metric("Temperature", f"Min: {min(temperatures):.2f} °C, Max: {max(temperatures):.2f} °C", "-")

# Continue with existing metrics
b2.metric("Electricity Price", f"{electricity_prices[0]:.2f} $/kWh", "-")
b3.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed
b4.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed

# Row C
c1, c2 = st.columns((7, 3))
with c1:
    st.markdown('### Temperature Trend')
    # Replace this with your actual line chart or visualization for temperature
    st.line_chart(pd.DataFrame({'Temperature': temperatures}, index=pd.date_range(start='2023-12-01', periods=30)))
with c2:
    st.markdown('### Electricity Price Trend')
    # Replace this with your actual line chart or visualization for electricity prices
    st.line_chart(electricity_prices)

# Row D
d1, d2 = st.columns((7, 3))
with d1:
    st.markdown('### Combined Trends')
    # Replace this with your actual line chart or visualization for both temperature and electricity prices
    combined_data = pd.DataFrame({
        'Temperature': temperatures,
        'Electricity Price': electricity_prices,
    }, index=pd.date_range(start='2023-12-01', periods=30))
    st.line_chart(combined_data)
with d2:
    st.markdown('### Statistics')
    # Replace this with any statistics or summary you want to display
    st.text(f"Average Temperature: {np.mean(temperatures):.2f} °C")
    st.text(f"Average Electricity Price: {np.mean(electricity_prices):.2f} $/kWh")
