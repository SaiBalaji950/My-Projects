from flask import Flask, render_template, redirect, request, url_for, flash, session
import pickle
import numpy as np
import pandas as pd
from collections import Counter
app = Flask(__name__)
app.secret_key = 'abcd1234'

model = pickle.load(open('model.pickle','rb'))
scaler = pickle.load(open('scaler.pickle','rb'))
users = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_registration',methods =['GET','POST'])
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
            float(request.form['max']),
            float(request.form['min']),
            float(request.form['mean']),
            float(request.form['sd']),
            float(request.form['rms']),
            float(request.form['skewness']),
            float(request.form['kurtosis']),
            float(request.form['crest']),
            float(request.form['form'])
        ]
        
        data_scaled = scaler.transform([data])
        prediction = model.predict(data_scaled)
        
        predicted_index = prediction[0]
        predicted_values = {
            0: 'Ball_007_1',
            1: 'Ball_014_1',
            2: 'Ball_021_1',
            3: 'IR_007_1',
            4: 'IR_014_1',
            5: 'IR_021_1',
            6: 'Normal_1',
            7: 'OR_007_6_1',
            8: 'OR_014_6_1',
            9: 'OR_021_6_1'
        }
        predicted_label = predicted_values.get(predicted_index, 'Unknown')
        return render_template('result.html', fault=predicted_label)
    except ValueError as ve:
        return f"Invalid input value: {str(ve)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
@app.route('/performance')
def performance():
    try:
        df = pd.read_csv('feature_time_48k_2048_load_1.csv') 
        fault_counts = df['fault'].value_counts()
        labels = fault_counts.index.tolist()
        values = fault_counts.values.tolist()
        return render_template('performance.html', labels=labels, values=values)
    except Exception as e:
        return f"An error occurred while loading performance data: {str(e)}"

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)