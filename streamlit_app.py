import streamlit as st
from PIL import Image
import pandas as pd
import requests
import numpy as np

# Function to get weather data from the external API
def get_weather_data(city):
    api_key = '46b2788544324cc8ada143152230512'  # Replace with your actual weather API key
    response = requests.get(f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=30')
    return response.json()['forecast']['forecastday']

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
        # Use an appropriate graph for temperature, e.g., line chart or area chart
        st.line_chart(pd.DataFrame({'Temperature': temperatures}, index=dates))
    else:
        st.warning("Temperature data not available")
with c2:
    st.markdown('### Electricity Price Trend')
    # Replace this with your actual line chart or visualization for electricity prices
    st.line_chart([round(np.random.uniform(0.10, 0.50), 2) for _ in range(30)])

# Row D
d1, d2 = st.columns((7, 3))
with d1:
    st.markdown('### Statistics')
    # Replace this with any statistics or summary you want to display
    if temperatures:
        st.text(f"Average Temperature: {round(np.mean(temperatures), 2)} °C")
        st.text(f"Average Electricity Price: {round(np.mean([np.random.uniform(0.10, 0.50) for _ in range(30)]), 2)} $/kWh")
    else:
        st.warning("Statistics not available")
with d2:
    pass  # Removed the content of the second column (previously combined trend)
