<h1>Weather Forecast Telegram Bot</h1>

<h2>Description</h2>
Telegram bot that predicts the weather type (sunny, rain, snow, etc.) in a selected city using data from the OpenWeatherMap API and a trained ML model (RandomForestClassifier).

<h3>Project structure</h3>

project/

├─ Data/

│   └─ weather_classification_data.csv      # CSV file with training data

├─ Model/

│   ├─ train_model.py                       # Training and saving the model

│   ├─ model.joblib                         # Trained model

│   └─ label_encoder.joblib                 # Class Encoder

├─ Bot/

│   └─ weather_bot.py                       # Telegram-bot

└─ README.md

<h2>Explanation of how the code works</h2>
<h3>train_model.py</h3> 
1.Loads the weather_classification_data.csv dataset from the ../Data/ folder.

2.Selects the desired features:
Temperature, Humidity, Wind Speed, Atmospheric Pressure, Visibility (km), Cloud Cover

3.Processes data:
Divides humidity by 100 (from percent → to fraction).
Encodes the target feature Weather Type via LabelEncoder (e.g. "Rain" → 1, "Clear" → 0, etc.).
Transforms the Cloud Cover categorical feature via OneHotEncoder.

4.Creates a Pipeline that includes:
ColumnTransformer for feature processing
RandomForestClassifier for classification

5.Splits data into train/test, trains the model, evaluates quality (outputs classification_report).

6.Saves the model and encoder:
model.joblib — trained model
label_encoder.joblib — class label encoder

<h3>bot.py</h3>
1. Loads the bot token and weather API key.

2. Loads the model and encoder created in train_model.py.

3. Processes Telegram commands:
/start — greeting
any message — is considered a city, the bot makes a forecast

4.Gets geolocation by city name via OpenWeatherMap Geo API.

5.Gets weather data (temperature, pressure, cloudiness, etc.).

6.Converts data to the required format and makes a weather prediction using the model.

7.Generates a response and sends to the user:
city, country
temperature, humidity, cloudiness
model prediction: for example, "Rain"





































