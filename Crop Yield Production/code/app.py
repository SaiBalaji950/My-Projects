from flask import Flask, render_template, request, session, redirect, url_for, flash
import pickle
import numpy as np
import pandas as pd
from collections import Counter

app = Flask(__name__)
app.secret_key = 'abcd123'

model = pickle.load(open('model.pickle', 'rb'))
scaler = pickle.load(open('scaler.pickle', 'rb'))
users = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('user_registration'))
        
        if username not in users:
            users[username] = {'password': password}
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user_login'))
        else:
            flash('User already exists', 'error')
            return redirect(url_for('user_registration'))
    
    return render_template('user_registration.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash('Successfully logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('user_login'))
    
    return render_template('user_login.html')

@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        flash('You need to log in first', 'error')
        return redirect(url_for('user_login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    try:
        data = [
            float(request.form['Nitrogen']),
            float(request.form['Phosphorus']),
            float(request.form['Potassium']),
            float(request.form['Temperature']),
            float(request.form['Humidity']),
            float(request.form['pH_Value']),
            float(request.form['Rainfall']),
            float(request.form['Yield'])
        ]

        data_scaled = scaler.transform([data])
        prediction = model.predict(data_scaled)

        predicted_index = prediction[0]  
        return render_template('result.html', crop=predicted_index)
    except ValueError as ve:
        return f"Invalid input value: {str(ve)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
@app.route('/performance')
def performance():
    df = pd.read_csv('Crop_Yield_Prediction.csv')
    crop_counts = Counter(df['Crop'])
    labels = list(crop_counts.keys())    
    values = list(crop_counts.values())  
    return render_template('performance.html', labels=labels, values=values)
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
