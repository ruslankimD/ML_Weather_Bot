import pandas as pd
import os
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# Upload CSV
csv_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'weather_classification_data.csv')
df = pd.read_csv(csv_path)

# Columns
features = ['Temperature', 'Humidity', 'Wind Speed', 'Atmospheric Pressure', 'Visibility (km)', 'Cloud Cover']
target = 'Weather Type'
df_filtered = df[features + [target]].copy() #removes all unnecessary data that interferes with the model training.
df_filtered['Humidity'] = df_filtered['Humidity'] / 100

# Variable encoding
label_encoder = LabelEncoder() #converts class strings to numbers
df_filtered['Weather Type Encoded'] = label_encoder.fit_transform(df_filtered['Weather Type'])

# OneHot for Cloud Cover
categorical = ['Cloud Cover']
numeric = ['Temperature', 'Humidity', 'Wind Speed', 'Atmospheric Pressure', 'Visibility (km)']

#ColumnTransformer handles different types of data
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
    ('num', 'passthrough', numeric)
])

#  Model and Pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])
# Divide the data into training and testing
X = df_filtered[features]
y = df_filtered['Weather Type Encoded']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# Model evaluation
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Saving the model and encoder
joblib.dump(pipeline, os.path.join(os.path.dirname(__file__), 'model.joblib'))
joblib.dump(label_encoder, os.path.join(os.path.dirname(__file__), 'label_encoder.joblib'))
