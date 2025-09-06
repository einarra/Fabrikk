document.getElementById('fetch-quote').addEventListener('click', fetchQuote);

function fetchQuote() {
    fetch('http://localhost:8000/api/quotes/random') // Replace with your FastAPI URL
        .then(response => response.json())
        .then(data => {
            document.getElementById('quote-display').innerText = data.quote;
        })
        .catch(error => {
            console.error('Error fetching quote:', error);
        });
}