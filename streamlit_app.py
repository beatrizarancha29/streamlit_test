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

# Page setting
st.set_page_config(layout="wide")
st.title( " Smart Home Heating System Dashboard")
import streamlit as st

# Set the background color to blue
import streamlit as st

# Set the background color to blue
st.markdown(
    """
    <style>
        .red-box {
            background-color: #e74c3c;
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: left;
            font-weight: bold;
            font-size: 24px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Create a div with the specified class and display the text "Barcelona"
st.markdown('<div class="red-box">Barcelona</div>', unsafe_allow_html=True)


# Here starts the web app design
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
    st.session_state.count = 0
else:
    st.session_state.count = 1

# Row B
b1, b2 = st.columns(2)

# Fetch weather data for the entire month in Barcelona
city_name = "Barcelona"  # Dynamically set to Barcelona
weather_data = get_weather_data(city_name)

# Extract temperature and date data from the API response
temperatures = [day['day'].get('avgtemp_c') for day in weather_data if 'day' in day and 'avgtemp_c' in day['day']]
dates = [day['date'] for day in weather_data if 'date' in day]

# Update the Temperature metric to display the entire month's forecast
st.markdown(
    """
    <style>
        .blue-box {
            background-color: #3498db;
            padding: 20px;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Set the background color to green
st.markdown(
    """
    <style>
        .green-box {
            background-color: #2ecc71;
            padding: 20px;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the blue and green boxes next to each other

with b1:
    with st.container():
        with st.expander("Temperature Metrics", expanded=True):
            temperatures = [20.5, 25.0, 18.2]  # Example temperature data
            if temperatures:
                st.markdown('<div class="blue-box">Min: {:.2f} °C, Max: {:.2f} °C</div>'.format(min(temperatures), max(temperatures)), unsafe_allow_html=True)
            else:
                st.warning("Temperature data not available")

with b2:
    with st.container():
        with st.expander("Electricity Metrics", expanded=True):
            st.markdown('<div class="green-box">Current Electricity Price: {} €/kWh</div>'.format(get_electricity_price_for_date(datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.now().hour)), unsafe_allow_html=True)


# Row C
c1, c2 = st.columns((7, 3))
with c1:
    st.markdown('### Temperature Trend Barcelona for the next 3 days')
    if temperatures:
        # Use an appropriate graph for temperature, e.g., line chart or area chart
        st.line_chart(pd.DataFrame({'Temperature': temperatures}, index=dates))
    else:
        st.warning("Temperature data not available")
c2.image('barcelona')
# Row D
# Fetch electricity prices for the previous day
yesterday = datetime.datetime.now() - datetime.timedelta(days=0)
previous_day = yesterday.strftime('%Y-%m-%d')
hours_of_day = range(24)
prices = []

# Button to call the price API
fetch_button_pressed = st.button("Fetch Electricity Prices")
if fetch_button_pressed:
    for hour in hours_of_day:
        price = get_electricity_price_for_date(previous_day, hour)
        print(f"The electricity price for {previous_day} {hour} is {price} €/kWh at {hour}:00.")

        # Append the price to the array
        prices.append(price)

st.markdown('### Electricity Price Trend')
if fetch_button_pressed:
    plt.plot(hours_of_day, prices, marker='o')
    plt.title(f'Electricity Prices on {previous_day}')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Electricity Price (€/kWh)')
    st.pyplot(plt)
else:
    st.warning("Please press the 'Fetch Electricity Prices' button.")


# Button to access the Receiver Statistics page
if st.button("Receiver Statistics"):
    webbrowser.open_new_tab("http://www.xyz.com")
