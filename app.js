const API_KEY = '6YAR8W4D56ZHXWYF';
const BASE_URL = 'https://www.alphavantage.co/query';

// Function to fetch stock prices from Alpha Vantage
async function getStockPrice(symbol) {
    const response = await fetch(`${BASE_URL}?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${API_KEY}`);
    const data = await response.json();
    const price = parseFloat(data['Global Quote']['05. price']);
    return price;
}

// Function to load user credits from JSON file
function loadCredits() {
    fetch('scores.json')
        .then(response => response.json())
        .then(data => {
            document.getElementById('credits').textContent = data.scores;
        });
}

// Function to save user credits to JSON file
function saveCredits(credits) {
    fetch('scores.json', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scores: credits })
    });
}

// Function to buy stocks
async function buyStock() {
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

    // Save the updated credits
    saveCredits(credits);
}

// Function to sell stocks
async function sellStock() {
    const symbol = document.getElementById('company').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const price = await getStockPrice(symbol);
    const gain = price * quantity;
    
    const creditsElement = document.getElementById('credits');
    let credits = parseFloat(creditsElement.textContent);

    credits += gain;
    creditsElement.textContent = credits;

    // Save the updated credits
    saveCredits(credits);
}

// Load user credits when the page loads
window.onload = loadCredits;
