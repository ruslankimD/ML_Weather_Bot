import telebot
import joblib
import os
import pandas as pd
from telebot import types
from weather import get_weather_data

# Settings
token = '8056737091:AAHdNSb4NZIs2HJy3opp4l_pTXIuCCMUHPM'
bot = telebot.TeleBot(token)

# Loading model and encoder
model_path = os.path.join(os.path.dirname(__file__), '..', 'Model', 'model.joblib')
encoder_path = os.path.join(os.path.dirname(__file__), '..', 'Model', 'label_encoder.joblib')

model = joblib.load(model_path)
label_encoder = joblib.load(encoder_path)

# Dictionary of icons for visualizing predictions
weather_icons = {
    "Sunny": "☀️",
    "Rainy": "🌧️",
    "Cloudy": "☁️",
    "Snowy": "❄️",
    "Stormy": "🌩️",
    "Clear": "🌤️"
}

# Menu commands
@bot.message_handler(commands=['start'])
def start_message(message):
    first_name = message.from_user.first_name

    # Start button
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn0 = types.KeyboardButton("▶️ Start")
    markup.add(btn0)

    bot.send_message(
        message.chat.id,
        f"Welcome, {first_name}! 👋\n"
        f"Press ▶️ Start to open the menu.",
        reply_markup=markup
    )

# Handling the Start button click
@bot.message_handler(func=lambda message: message.text == "▶️ Start")
def show_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("/forecast")
    btn2 = types.KeyboardButton("/help")
    btn3 = types.KeyboardButton("/about")
    markup.add(btn1, btn2, btn3)

    bot.send_message(
        message.chat.id,
        "📌 Menu opened! Choose a command:",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(
        message.chat.id,
        "❓ How to use:\n"
        "1️⃣ Enter the name of a city (e.g., Tashkent).\n"
        "2️⃣ I will show you the current weather data and predict the type of weather.\n\n"
        "📌 Commands:\n"
        "/start — Start bot\n"
        "/forecast — Forecast by city\n"
        "/about — About this project"
    )

@bot.message_handler(commands=['about'])
def about_message(message):
    bot.send_message(
        message.chat.id,
        "🤖 *ML Weather Bot*\n"
        "This bot uses OpenWeatherMap API 🌍 and a Machine Learning model (RandomForest) to predict the weather.\n\n"
        "Author: Ruslan",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['forecast'])
def forecast_message(message):
    bot.send_message(message.chat.id, "🌍 Please enter the name of the city:")
    bot.register_next_step_handler(message, handle_message)

# Basic logic of prediction
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Receive the text of the message from the user
    city = message.text.strip()

    # If the user pressed a command button, we will process it separately
    if city.startswith("/"):
        if city == "Start":
            start_message(message)
        elif city == "Forecast":
            forecast_message(message)
        elif city == "Help":
            help_message(message)
        elif city == "About":
            about_message(message)
        return

    # Get weather data for the specified city
    weather_features = get_weather_data(city)
    if not weather_features:
        bot.send_message(message.chat.id, "❌ Unable to get weather for this city. Make sure you entered a real city. (No grammatical errors).")
        return

    # Preparing data for the model
    x = pd.DataFrame([{
        'Temperature': weather_features['Temperature'],
        'Humidity': weather_features['Humidity'],
        'Wind Speed': weather_features['Wind Speed'],
        'Atmospheric Pressure': weather_features['Atmospheric Pressure'],
        'Visibility (km)': weather_features['Visibility (km)'],
        'Cloud Cover': weather_features['Cloud Cover']
    }])

    # Predicting weather type using a model
    prediction = model.predict(x)
    label = label_encoder.inverse_transform(prediction)[0]  # Convert the numeric prediction back to a string

    # Selecting an icon for prediction
    icon = weather_icons.get(label.capitalize(), "❓")

    # Form a message with data and prediction
    response = (
        f"📊 DATA\n"
        f"🌍 City: {weather_features['City']}, {weather_features['Country']}\n"
        f"🌡 Temperature: {weather_features['Temperature']} °C\n"
        f"💧 Humidity: {int(weather_features['Humidity'] * 100)}%\n"
        f"☁️ Cloud Cover: {weather_features['Cloud Cover'].capitalize()}\n"
        f"💨 Wind Speed: {round(weather_features['Wind Speed'], 1)} км/ч\n"
        f"✅ The model predicts: {icon} {label.capitalize()}"
    )
    bot.send_message(message.chat.id, response)

print("Bot Launched...")
bot.polling()

