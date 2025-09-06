const app = document.getElementById('app');

async function fetchQuotes() {
    try {
        const response = await fetch('http://localhost:8000/quotes'); // Replace with your API endpoint
        const quotes = await response.json();
        displayQuotes(quotes);
    } catch (error) {
        console.error('Error fetching quotes:', error);
    }
}

function displayQuotes(quotes) {
    if (!quotes || quotes.length === 0) {
        app.innerHTML = '<p>No quotes found.</p>';
        return;
    }
    app.innerHTML = quotes.map(quote => `<div class='quote'>${quote}</div>`).join('');
}

fetchQuotes();