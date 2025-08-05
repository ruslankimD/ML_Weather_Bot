import telebot
import requests
import joblib
import os
import pandas as pd

# Settings
token = '8056737091:AAHdNSb4NZIs2HJy3opp4l_pTXIuCCMUHPM'
weather_api = '989df811983562dee7aa1bb81c552ab3'

bot = telebot.TeleBot(token)

# Loading model and encoder
model_path = os.path.join(os.path.dirname(__file__), '..', 'Model', 'model.joblib')
encoder_path = os.path.join(os.path.dirname(__file__), '..', 'Model', 'label_encoder.joblib')

model = joblib.load(model_path)
label_encoder = joblib.load(encoder_path)

# Getting coordinates by city name
def get_coordinates(city):
    city_input = city.strip().lower()
    #Checking title length:
    if len(city_input) < 3:
        return None

    #Checking the response from the API
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={weather_api}"
    res = requests.get(geo_url)
    if res.status_code != 200:
        return None

    #Checking for data availability
    data = res.json()
    if not data:
        return None

    #Checking if the entered city matches the found one
    result = data[0]
    api_city = result.get('name', '').strip().lower()
    if api_city != city_input and city_input not in api_city and api_city not in city_input:
        return None

    #Checking country availability
    if 'country' not in result:
        return None

    return result['lat'], result['lon'], result['name'], result['country']

# Getting weather by coordinates
def get_weather_data(city):
    # Get city coordinates via geo-API
    coords = get_coordinates(city)
    if not coords:
        return None
    lat, lon, real_city_name, country_code = coords

    # Generate URL to get weather data by coordinates
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api}&units=metric'
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()

    try:
        # Extract the required weather data from the API response
        temp = data['main']['temp'] # Temperature in degrees Celsius
        humidity = data['main']['humidity'] / 100 # Humidity (in fractions, 0.0–1.0)
        wind_speed = data['wind']['speed'] * 3.6 # Wind speed: m/s → km/h
        pressure = data['main']['pressure']
        visibility = data.get('visibility', 10000) / 1000 # Visibility in km, default 10 km
        cloudiness = data['clouds']['all'] # Cloudiness in %

        # Classify clouds into categories
        if cloudiness < 25:
            cloud_cover = 'clear'
        elif cloudiness < 70:
            cloud_cover = 'partly cloudy'
        else:
            cloud_cover = 'overcast'
        # Return a dictionary with features for the model and data for display
        return {
            'City': real_city_name,
            'Country': country_code,
            'Temperature': temp,
            'Humidity': humidity,
            'Wind Speed': wind_speed,
            'Atmospheric Pressure': pressure,
            'Visibility (km)': visibility,
            'Cloud Cover': cloud_cover
        }
    except KeyError:
        return None

# Command processing
@bot.message_handler(commands=['start'])
def start_message(message):
    first_name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"Welcome, {first_name}! 👋\nSend me the name of a city (only in English), and I will predict the weather."
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Receive the text of the message from the user
    city = message.text.strip()
    #Get weather data for the specified city
    weather_features = get_weather_data(city)
    if not weather_features:
        bot.send_message(message.chat.id, "❌ Unable to get weather for this city. Make sure you entered a real city. (No grammatical errors).")
        return

    # Preparing data for the model
    X = pd.DataFrame([{
        'Temperature': weather_features['Temperature'],
        'Humidity': weather_features['Humidity'],
        'Wind Speed': weather_features['Wind Speed'],
        'Atmospheric Pressure': weather_features['Atmospheric Pressure'],
        'Visibility (km)': weather_features['Visibility (km)'],
        'Cloud Cover': weather_features['Cloud Cover']
    }])
    #Predicting weather type using a model
    prediction = model.predict(X)
    label = label_encoder.inverse_transform(prediction)[0] #Convert the numeric prediction back to a string

    #Form a message with data and prediction
    response = (
        f"📊 DATA\n"
        f"🌍City: {weather_features['City']}, {weather_features['Country']}\n"
        f"🌡️Temperature: {weather_features['Temperature']} °C\n"
        f"💧Humidity: {int(weather_features['Humidity'] * 100)}%\n"
        f"☁️Cloud Cover: {weather_features['Cloud Cover'].capitalize()}\n"
        f"💨Wind Speed: {round(weather_features['Wind Speed'], 1)} км/ч\n"
        f"✅The model predicts: {label.capitalize()}"
    )

    bot.send_message(message.chat.id, response)

print("Bot Launched...")
bot.polling()

