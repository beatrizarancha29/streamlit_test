import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Dummy data for illustration (replace this with your actual data)
temperature_data = pd.DataFrame({
    'date': pd.date_range(start='2023-12-01', end='2023-12-30'),
    'temperature': [math.sin(math.pi * i / 15) * 20 + 50 for i in range(30)],
})

electricity_prices = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55,
                               0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.85, 0.80, 0.75,
                               0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25])

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
b1.metric("Temperature", f"{temperature_data['temperature'][0]:.2f} °F", "-")
b2.metric("Electricity Price", f"{electricity_prices[0]:.2f} $/kWh", "-")
b3.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed
b4.metric("Humidity", "-", "-")  # Replace with actual data or remove if not needed

# Row C
c1, c2 = st.columns((7, 3))
with c1:
    st.markdown('### Temperature Trend')
    # Replace this with your actual line chart or visualization for temperature
    st.line_chart(temperature_data.set_index('date')['temperature'])
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
        'Temperature': temperature_data['temperature'],
        'Electricity Price': electricity_prices,
    }, index=temperature_data['date'])
    st.line_chart(combined_data)
with d2:
    st.markdown('### Statistics')
    # Replace this with any statistics or summary you want to display
    st.text(f"Average Temperature: {temperature_data['temperature'].mean():.2f} °F")
    st.text(f"Average Electricity Price: {np.mean(electricity_prices):.2f} $/kWh")
