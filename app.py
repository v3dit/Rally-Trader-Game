from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
import json
import threading
import subprocess

app = Flask(__name__, template_folder="templates")
#pk_85f77d6f509e4b2ab7621d09fc0903e3
API_KEY = 'pk_e504b12037a24f959798ac7e53538b3d'
BASE_URL = 'https://cloud.iexapis.com/stable'
PORTFOLIO_FILE = 'scores.json'

# Function to fetch stock prices from IEX Cloud
def get_stock_price(symbol):
    response = requests.get(f"{BASE_URL}/stock/{symbol}/quote?token={API_KEY}")
    data = response.json()
    # Check if the expected properties exist in the response object
    if not data or 'latestPrice' not in data:
        raise Exception('Failed to fetch stock price')
    return data['latestPrice']

# Function to load user data from JSON file
def load_user_data(username):
    if not os.path.exists(PORTFOLIO_FILE):
        return {}
    with open(PORTFOLIO_FILE) as f:
        data = json.load(f)
        return data.get(username, {})

# Function to save user data to JSON file
def save_user_data(username, data):
    with open(PORTFOLIO_FILE, 'r') as f:
        all_data = json.load(f)
    all_data[username] = data
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)

# Run the Pygame game
def run_pygame_game():
    subprocess.run(['python', 'main.py'])

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    username = request.form.get("username")
    return render_template('index.html', username=username)

# Route to handle user data
@app.route('/user/<username>', methods=['GET', 'POST', 'PUT'])
def handle_user(username):
    if request.method == 'GET':
        user_data = load_user_data(username)
        return jsonify(user_data)
    elif request.method == 'POST' or request.method == 'PUT':
        data = request.json
        save_user_data(username, data)
        return 'User data saved successfully'

@app.route('/<userName>/stocks')
def stocks(userName):
    # Define the symbols of the stocks you want to fetch data for
    symbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB', 'TSLA', 'BRK.A', 'NVDA', 'JPM', 'JNJ',
        'V', 'MA']# 'PYPL', 'WMT', 'PG', 'BABA', 'UNH', 'HD', 'DIS', 'CRM','XOM', 'NFLX', 'CMCSA', 'VZ', 'CVX']  
    # Add more symbols as needed
    
    # Load user data from the stores.json file
    with open('scores.json') as f:
        user_data = json.load(f)

    stock_data = []

    for symbol in symbols:
        try:
            response = requests.get(f"{BASE_URL}/stock/{symbol}/quote?token={API_KEY}")
            if response.status_code == 200:
                data = response.json()
                stock_info = {
                    'name': data['companyName'],
                    'symbol': data['symbol'],
                    'price': data['latestPrice'],
                    'owned': user_data.get(userName, {}).get('portfolio', {}).get(symbol, 0)
                }# Add more relevant data here
                stock_data.append(stock_info)
            else:
                return jsonify({'error': 'Failed to fetch stock data'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    return jsonify(stock_data)


# Route to buy stocks
@app.route('/buy', methods=['POST'])
def buy_stock():
    data = request.json
    username = data.get('username')
    symbol = data.get('symbol')
    quantity = float(data.get('quantity'))
    try:
        price = get_stock_price(symbol)
        cost = price * quantity
        user_data = load_user_data(username)
        credits = user_data.get('credits', 0)
        if cost > credits:
            return 'Not enough credits!', 400
        user_data['credits'] -= cost
        user_data['portfolio'][symbol] = user_data['portfolio'].get(symbol, 0) + quantity
        save_user_data(username, user_data)
        return 'Stock bought successfully'
    except Exception as e:
        return str(e), 500

# Route to sell stocks
@app.route('/sell', methods=['POST'])
def sell_stock():
    data = request.json
    username = data.get('username')
    symbol = data.get('symbol')
    quantity = float(data.get('quantity'))
    try:
        price = get_stock_price(symbol)
        gain = price * quantity
        user_data = load_user_data(username)
        portfolio = user_data.get('portfolio', {})
        if symbol not in portfolio or portfolio[symbol] < quantity:
            return 'Not enough stocks to sell!', 400
        user_data['credits'] += gain
        user_data['portfolio'][symbol] -= quantity
        save_user_data(username, user_data)
        return 'Stock sold successfully'
    except Exception as e:
        return str(e), 500

# Function to update user data
@app.route('/update', methods=['PUT'])
def update_user_data():
    data = request.json
    username = data.get('username')
    new_data = data.get('new_data')
    try:
        user_data = load_user_data(username)
        user_data.update(new_data)
        save_user_data(username, user_data)
        return 'User data updated successfully'
    except Exception as e:
        return str(e), 500

# Route to run the game
@app.route('/run_game')
def run_game():
    threading.Thread(target=run_pygame_game).start()
    return 'Game is running...' #render_template('index.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
