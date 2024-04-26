from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

API_KEY = 'pk_1671fce8db02437bb8edb8fa29ae6197'
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
        
app = Flask(__name__, template_folder="templates")

@app.route('/user/<username>', methods=['GET', 'POST', 'PUT'])
def handle_user(username):
    if request.method == 'GET':
        user_data = load_user_data(username)
        return jsonify(user_data)
    elif request.method == 'POST':
        data = request.json
        save_user_data(username, data)
        return 'User data saved successfully'
    elif request.method == 'PUT':
        data = request.json
        save_user_data(username, data)
        return 'User data updated successfully'

@app.route('/stock/<symbol>/price', methods=['GET'])
def get_stock_price_endpoint(symbol):
    try:
        price = get_stock_price(symbol)
        return jsonify({'price': price})
    except Exception as e:
        return str(e), 500

# Function to buy stocks
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

# Function to sell stocks
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

# Serve the HTML page
@app.route('/')
def index():
    with open('index.html') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True)
