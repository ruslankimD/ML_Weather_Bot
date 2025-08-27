import telebot
import joblib
import os
import pandas as pd
from weather import get_weather_data

# Settings
token = '8056737091:AAHdNSb4NZIs2HJy3opp4l_pTXIuCCMUHPM'
bot = telebot.TeleBot(token)

# Loading model and encoder
model_path = os.path.join(os.path.dirname(__file__), '..', 'Model', 'model.joblib')
encoder_path = os.path.join(os.path.dirname(__file__), '..', 'Model', 'label_encoder.joblib')

model = joblib.load(model_path)
label_encoder = joblib.load(encoder_path)

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
        f"🌡Temperature: {weather_features['Temperature']} °C\n"
        f"💧Humidity: {int(weather_features['Humidity'] * 100)}%\n"
        f"☁️Cloud Cover: {weather_features['Cloud Cover'].capitalize()}\n"
        f"💨Wind Speed: {round(weather_features['Wind Speed'], 1)} км/ч\n"
        f"✅The model predicts: {label.capitalize()}"
    )
    bot.send_message(message.chat.id, response)

print("Bot Launched...")
bot.polling()

