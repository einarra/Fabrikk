document.getElementById('fetchQuote').addEventListener('click', fetchQuote);

async function fetchQuote() {
    try {
        const response = await fetch('http://localhost:8000/api/quotes');
        const data = await response.json();
        document.getElementById('quoteDisplay').innerText = data.quote;
    } catch (error) {
        console.error('Error fetching quote:', error);
        document.getElementById('quoteDisplay').innerText = 'Failed to fetch quote.';
    }
}