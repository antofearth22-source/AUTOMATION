// backend/providers/skyscanner-provider.js
const axios = require('axios');
const config = require('../config.json');

/**
 * Mock provider for Skyscanner.
 *
 * @param {object} searchParams - The flight search parameters (origin, destination, date).
 * @param {object} country - The country configuration object.
 * @returns {Promise<Array<object>>} A promise that resolves to an array of flight results.
 */
async function search(searchParams, country) {
  console.log(`[Skyscanner] Searching for flights from ${country.name} with params:`, searchParams);

  // --- Proxy Configuration ---
  const proxyHost = `proxy.${country.code.toLowerCase()}.example.com`;
  const proxyPort = 8080;
  const proxyUsername = config.proxy.username;
  const proxyPassword = config.proxy.password;

  const axiosConfig = {
    proxy: {
      host: proxyHost,
      port: proxyPort,
      auth: {
        username: proxyUsername,
        password: proxyPassword
      }
    }
  };

  // In a real implementation, you would use axios to make a request to the Skyscanner API:
  // const response = await axios.get('https://api.skyscanner.net/v3/flights/live/search/create', { ...axiosConfig, params: { ... } });
  // For now, we will just simulate the request and return mock data.


  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

  // Determine currency based on country
  let currency, amount;
  switch (country.code) {
    case 'GB':
      currency = 'GBP';
      amount = Math.floor(350 + Math.random() * 150);
      break;
    case 'IN':
      currency = 'INR';
      amount = Math.floor(30000 + Math.random() * 10000);
      break;
    case 'DE':
    case 'FR':
      currency = 'EUR';
      amount = Math.floor(400 + Math.random() * 180);
      break;
    default:
      currency = 'USD';
      amount = Math.floor(420 + Math.random() * 220);
  }

  // Return realistic, hard-coded sample data
  return [
    {
      provider: 'Skyscanner',
      origin: searchParams.origin,
      destination: searchParams.destination,
      date: searchParams.date,
      price: {
        amount,
        currency,
      },
      bookingLink: `https://www.skyscanner.net/transport/flights/${searchParams.origin}/${searchParams.destination}/${searchParams.date}/`
    }
  ];
}

module.exports = {
  search
};
