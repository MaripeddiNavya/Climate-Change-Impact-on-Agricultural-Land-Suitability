from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import joblib
import numpy as np
import json
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Load the trained model
model = joblib.load('gradient_boosting_model_pipeline.pkl')

# File to store user data
USER_FILE = 'users.json'

# Load users from the file
def load_users():
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save users to the file
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('predict'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            return "User already exists! Please log in."
        
        # Store hashed password
        users[username] = generate_password_hash(password)
        save_users(users)  # Save to file
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('predict'))
        else:
            return "Invalid username or password."

    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    prediction_result = None  # Default value

    if request.method == 'POST':
        # Get input data from the form
        input_data = request.form.to_dict()


        

        # Convert the input data to a pandas DataFrame (so that you can refer to columns by names)
        data = {
            'Region': [input_data['Region']],
            'Elevation': [int(input_data['Elevation'])],
            'Slope': [float(input_data['Slope'])],
            'Aspect': [float(input_data['Aspect'])],
            'Soil Type': [input_data['Soil Type']],
            'Land Cover': [input_data['Land Cover']],
            'Avg Annual Temp': [float(input_data['Avg Annual Temp'])],
            'Avg Annual Precip': [int(input_data['Avg Annual Precip'])],
            'GDD': [int(input_data['GDD'])],
            'Seasonal Precip Variability': [float(input_data['Seasonal Precip Variability'])],
            'Solar Radiation': [float(input_data['Solar Radiation'])],
            'Wind Speed': [float(input_data['Wind Speed'])],
            'Humidity': [float(input_data['Humidity'])]
        }

        # Convert the data dictionary into a pandas DataFrame
        df = pd.DataFrame(data)

        prediction = model.predict(df)[0]

        # Redirect to the result page with the prediction
        return redirect(url_for('prediction_result', prediction=round(prediction, 2)))

    return render_template('predict_region.html')

@app.route('/prediction_result')
def prediction_result():
    # Retrieve the prediction from the query parameters
    prediction = request.args.get('prediction')
    return render_template('prediction_result.html', prediction=prediction)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)