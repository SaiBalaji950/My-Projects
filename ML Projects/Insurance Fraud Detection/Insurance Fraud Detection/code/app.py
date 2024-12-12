from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import pickle
import numpy as np
import pandas as pd
from collections import Counter

app = Flask(__name__)
app.secret_key = 'abcd123'  

# Load model and scaler
model = pickle.load(open('model.pickle', 'rb'))
scaler = pickle.load(open('scaler.pickle', 'rb'))
users = {}

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# User Registration Route
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

# User Login Route
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

# Main Page After Login
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
        # Collecting data from the form
        data = [
            float(request.form['WeekOfMonth']),
            float(request.form['Make']),
            float(request.form['AccidentArea']),
            float(request.form['DayOfWeekClaimed']),
            float(request.form['WeekOfMonthClaimed']),
            float(request.form['Sex']),
            float(request.form['MaritalStatus']),
            float(request.form['Age']),
            float(request.form['Fault']),
            float(request.form['PolicyType']),
            float(request.form['VehicleCategory']),
            float(request.form['VehiclePrice']),
            float(request.form['PolicyNumber']),
            float(request.form['Deductible']),
            float(request.form['Days_Policy_Accident']),
            float(request.form['Days_Policy_Claim']),
            float(request.form['PastNumberOfClaims']),
            float(request.form['AgeOfVehicle']),
            float(request.form['AgeOfPolicyHolder']),
            float(request.form['PoliceReportFiled']),
            float(request.form['WitnessPresent']),
            float(request.form['AgentType']),
            float(request.form['NumberOfSuppliments']),
            float(request.form['AddressChange_Claim']),
            float(request.form['NumberOfCars']),
            float(request.form['BasePolicy'])
        ]
        
        # Scale data before prediction
        data_scaled = scaler.transform([data])

        # Predict using the model without setting a custom threshold
        prediction = model.predict(data_scaled)
        output = 'Fraud' if prediction[0] == 1 else 'Legitimate (Not Fraud)'
        css_class = 'fraud' if output == 'Fraud' else 'legitimate'

        return render_template('result.html', prediction_text=f'The Policy Holder was {output}',css_class=css_class)
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/performance')
def performance():
    try:
        # Load dataset for analysis
        df = pd.read_csv('data.csv')
        fraud_counts = df['FraudFound_P'].value_counts()

        labels = ['Legitimate', 'Fraud']
        values = [fraud_counts.get(0, 0), fraud_counts.get(1, 0)]

        return render_template('performance.html', labels=labels, values=values)
    except Exception as e:
        return f"An error occurred while loading performance data: {str(e)}"


# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
