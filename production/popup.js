// frontend/popup.js

function run() {
  const searchButton = document.getElementById('search-button');
  const originInput = document.getElementById('origin');
  const destinationInput = document.getElementById('destination');
  const dateInput = document.getElementById('date');
  const dateFlexibilityInput = document.getElementById('date-flexibility');
  const stopsInput = document.getElementById('stops');
  const resultsDiv = document.getElementById('results');

  const API_URL = 'http://localhost:3000/search-flights';
  const API_KEY = 'A_SHARED_SECRET_KEY_FOR_EXTENSION_TO_USE';

  searchButton.addEventListener('click', async () => {
    const origin = originInput.value;
    const destination = destinationInput.value;
    const date = dateInput.value;
    const date_flexibility = parseInt(dateFlexibilityInput.value, 10);
    const stops = stopsInput.value;

    if (!origin || !destination || !date) {
      resultsDiv.innerHTML = '<p style="color: red;">Please fill in all fields.</p>';
      return;
    }

    resultsDiv.innerHTML = '<div class="loading"><p>Searching for flights...</p></div>';

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
        },
        body: JSON.stringify({ origin, destination, date, date_flexibility, stops }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'An unknown error occurred.');
      }

      const flights = await response.json();
      renderResults(flights, resultsDiv);

    } catch (error) {
      resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
      console.error('Search failed:', error);
    }
  });
}

function renderResults(flights, resultsDiv) {
  if (flights.length === 0) {
    resultsDiv.innerHTML = '<p>No flights found.</p>';
    return;
  }

  let html = '';
  flights.forEach(flight => {
      html += `
      <div class="result-item">
        <h3>Book from ${flight.country.name}</h3>
        <p class="price">
          <strong>${flight.price.amount.toLocaleString()} ${flight.price.currency}</strong>
          (approx. ${flight.convertedPrice.amount.toLocaleString()} ${flight.convertedPrice.currency})
        </p>
        <button class="book-button" data-url="${flight.bookingLink}" data-country='${JSON.stringify(flight.country)}'>Book Now</button>
      </div>
    `;
  });

  resultsDiv.innerHTML = html;

  // Add event listeners to the new "Book Now" buttons
  document.querySelectorAll('.book-button').forEach(button => {
    button.addEventListener('click', (event) => {
      const url = event.target.dataset.url;
      const country = JSON.parse(event.target.dataset.country);
      chrome.runtime.sendMessage({
        action: 'bookFlight',
        payload: { url, country }
      });
    });
  });
}


if (typeof module !== 'undefined' && module.exports) {
  module.exports = { run, renderResults };
} else {
  run();
}
