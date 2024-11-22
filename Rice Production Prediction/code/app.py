from flask import Flask, render_template, redirect, url_for, session, request, flash
import pickle
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
            int(request.form['Year']),
            int(request.form['Harvested Area']),
            int(request.form['Production']),
            int(request.form['Rainfall']),
            int(request.form['Humidity']),
            int(request.form['Temperature'])
        ]
        
        data_scaled = scaler.transform([data])
        prediction = model.predict(data_scaled)
        province_names = [
    'Aceh', 'Kepulauan Riau', 'Sulawesi Utara', 'Jawa Timur', 'Jambi', 'Riau',
    'Nusa Tenggara Timur', 'Kalimantan Tengah', 'Kalimantan Barat', 'Bengkulu',
    'Papua Barat', 'Maluku Utara', 'Sumatera Utara', 'Banten', 'Gorontalo',
    'DI Yogyakarta', 'Kalimantan Selatan', 'Sulawesi Tenggara', 'Nusa Tenggara Barat',
    'Papua', 'Kalimantan Utara', 'Bali', 'Sumatera Selatan', 'Sulawesi Barat', 'Maluku',
    'Sulawesi Tengah', 'Kepulauan Bangka Belitung', 'Lampung', 'Jawa Tengah', 'Sulawesi Selatan',
    'DKI Jakarta', 'Sumatera Barat', 'Jawa Barat'
]
        
        predicted_index = prediction[0]
        predicted_province = province_names[int(prediction[0])]  
        return render_template('result.html', Province=predicted_province)

    except ValueError as ve:
        return f"Invalid input value: {str(ve)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
@app.route('/performance')
def performance():
    try:
        df = pd.read_csv('expanded_agriculture_data.csv') 
        province_counts = df['Province'].value_counts()
        labels = province_counts.index.tolist()
        values = province_counts.values.tolist()
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