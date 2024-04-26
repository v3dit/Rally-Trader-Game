// const API_KEY = '6YAR8W4D56ZHXWYF';
// const API_KEY = 'YAXID3YY1BSV1124';
// const API_KEY ="M6C9GD28AZ8GQKKG";
const BASE_URL = 'https://www.alphavantage.co/query';
const PORTFOLIO_FILE = 'scores.json';

// Function to fetch stock prices from Alpha Vantage
async function getStockPrice(symbol) {
    const response = await fetch(`${BASE_URL}?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${API_KEY}`);
    const data = await response.json();
    console.log(data)
    // Check if the expected properties exist in the response object
    if (!data || !data['Global Quote'] || !data['Global Quote']['05. price']) {
        throw new Error('Failed to fetch stock price');
    }
    const price = parseFloat(data['Global Quote']['05. price']);
    return price;
}


// Function to load user credits and portfolio from JSON file
function loadUserData(username) {
    fetch(PORTFOLIO_FILE)
        .then(response => response.json())
        .then(data => {
            const userData = data[username];
            document.getElementById('credits').textContent = userData.credits;
            document.getElementById('portfolio').innerHTML = ''; // Clear previous portfolio data
            Object.keys(userData.portfolio).forEach(symbol => {
                const quantity = userData.portfolio[symbol];
                displayPortfolioItem(symbol, quantity);
            });
        });
}

// Function to save user data (credits and portfolio) to JSON file
function saveUserData(username, userData) {
    fetch(PORTFOLIO_FILE)
        .then(response => response.json())
        .then(data => {
            data[username] = userData;
            return fetch(PORTFOLIO_FILE, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to save user data');
            }
        })
        .catch(error => {
            console.error('Error saving user data:', error);
        });
}


// Function to display portfolio item
function displayPortfolioItem(symbol, quantity) {
    const portfolioDiv = document.getElementById('portfolio');
    const item = document.createElement('div');
    item.textContent = `${symbol}: ${quantity}`;
    portfolioDiv.appendChild(item);
}

// Function to buy stocks
async function buyStock() {
    const username = prompt('Enter your username:');
    const symbol = document.getElementById('company').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const price = await getStockPrice(symbol);
    const cost = price * quantity;
    
    const creditsElement = document.getElementById('credits');
    let credits = parseFloat(creditsElement.textContent);

    if (cost > credits) {
        alert('Not enough credits!');
        return;
    }

    credits -= cost;
    creditsElement.textContent = credits;

    // Update portfolio
    const portfolioItem = { [symbol]: quantity };
    const userData = { username, credits, portfolio: portfolioItem };
    saveUserData(username, userData);

    // Update portfolio display
    displayPortfolioItem(symbol, quantity);
}

// Function to sell stocks
async function sellStock() {
    const username = prompt('Enter your username:');
    const symbol = document.getElementById('company').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const price = await getStockPrice(symbol);
    const gain = price * quantity;

    // Load user data
    const response = await fetch(PORTFOLIO_FILE);
    const data = await response.json();
    const userData = data[username];
    if (!userData) {
        alert('User not found!');
        return;
    }

    const creditsElement = document.getElementById('credits');
    let credits = parseFloat(creditsElement.textContent);

    if (userData.portfolio[symbol] < quantity) {
        alert('Not enough stocks to sell!');
        return;
    }

    credits += gain;
    creditsElement.textContent = credits;

    // Update portfolio
    userData.portfolio[symbol] -= quantity;
    saveUserData(username, userData);

    // Update portfolio display
    document.getElementById('portfolio').innerHTML = ''; // Clear previous portfolio data
    Object.keys(userData.portfolio).forEach(sym => {
        const qty = userData.portfolio[sym];
        displayPortfolioItem(sym, qty);
    });
}

// Load user data when the page loads
window.onload = () => {
    const username = prompt('Enter your username:');
    loadUserData(username);
};
