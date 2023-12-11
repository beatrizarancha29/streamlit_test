import numpy as np
import streamlit as st
from PIL import Image
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

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
def get_electricity_price_for_date(date, hour):
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
                    return price

            print(f"Error: 'values' key not found in 'attributes'. Response: {data}")
            return None
        else:
            print(f"Error: 'included' key not found in response. Response: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

# Find the electricity prices for yesterday and store them in an array
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
previous_day = yesterday.strftime('%Y-%m-%d')
hours_of_day = range(24)
prices = []

for hour in hours_of_day:
    price = get_electricity_price_for_date(previous_day, hour)
    print(f"The electricity price for {previous_day} {hour} is {price} €/MWh at {hour}:00.")
    
    # Append the price to the array
    prices.append(price)

# Plotting the prices against time
hours_range = [f'{hour}:00' for hour in hours_of_day]
plt.plot(hours_range, prices, marker='o')
plt.title(f'Electricity Prices on {previous_day}')
plt.xlabel('Hour of the Day')
plt.ylabel('Electricity Price (€/MWh)')
plt.show()

    except requests.exceptions.RequestException as e:
        st.error(f"Error making API request: {e}")
        return [], []

# Page setting
st.set_page_config(layout="wide")

# Fetch and apply custom style from 'style.css'
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
    b2.line_chart(pd.DataFrame({'Temperature': temperatures_day}, index=hours_day))
else:
    b2.warning("Temperature data not available for the day")

# Continue with existing metrics
real_time_prices, real_time_times = get_electricity_prices()
if real_time_prices:
    b3.metric("Electricity Price", f"{round(min(real_time_prices), 2)} - {round(max(real_time_prices), 2)} $/kWh", "")

    # Plot the real-time electricity prices for the day
    df_prices = pd.DataFrame({'Time': real_time_times, 'Price': real_time_prices})

    # Ensure the 'Time' column is in a format that can be parsed to datetime
    try:
        df_prices['Time'] = pd.to_datetime(df_prices['Time'])
    except pd.errors.OutOfBoundsDatetime:
        st.error("Error: Out of bounds nanosecond timestamp in 'Time' column.")
        st.stop()

    # Convert 'Time' to numerical values
    df_prices['Time'] = date2num(df_prices['Time'])

    # Get the current hour to highlight in the plot
    current_hour = datetime.datetime.now().hour

    fig, ax = plt.subplots()
    ax.plot_date(df_prices['Time'], df_prices['Price'], fmt='o', label='Real-time Prices', color='blue')
    
    # Highlight the hour closest to the current time in red
    nearest_hour_index = np.argmin(np.abs(np.array([t.hour for t in pd.to_datetime(df_prices['Time'].values)]) - current_hour))
    ax.plot_date(df_prices['Time'][nearest_hour_index], df_prices['Price'][nearest_hour_index],
                 fmt='o', color='red', markersize=10, label=f'Current Hour: {current_hour}:00')

    ax.set_xlabel('Time')
    ax.set_ylabel('Electricity Price ($/kWh)')
    ax.set_title('Real-time Electricity Price Variation for the Day')
    ax.tick_params(rotation=45)
    ax.legend()
    st.pyplot(fig)
else:
    b3.warning("Real-time electricity price data not available for the day")

# Row C
c1, c2 = st.columns((7, 3))
with c1:
    st.markdown('### Temperature Trend for the Day')
    if temperatures_day:
        st.line_chart(pd.DataFrame({'Temperature': temperatures_day}, index=hours_day))
    else:
        st.warning("Temperature data not available for the day")
with c2:
    st.markdown('### Electricity Price Trend for the Day')

    # Get real-time electricity prices
    real_time_prices, real_time_times = get_electricity_prices()

    if real_time_prices:
        # Plot the real-time electricity prices for the day
        df_prices = pd.DataFrame({'Time': real_time_times, 'Price': real_time_prices})

        # Ensure the 'Time' column is in a format that can be parsed to datetime
        try:
            df_prices['Time'] = pd.to_datetime(df_prices['Time'])
        except pd.errors.OutOfBoundsDatetime:
            st.error("Error: Out of bounds nanosecond timestamp in 'Time' column.")
            st.stop()

        # Convert 'Time' to numerical values
        df_prices['Time'] = date2num(df_prices['Time'])

        fig, ax = plt.subplots()
        ax.plot_date(df_prices['Time'], df_prices['Price'], fmt='o', label='Real-time Prices')
        ax.set_xlabel('Time')
        ax.set_ylabel('Electricity Price ($/kWh)')
        ax.set_title('Real-time Electricity Price Variation for the Day')
        ax.tick_params(rotation=45)
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Real-time electricity price data not available for the day")

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
