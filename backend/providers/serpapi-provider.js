// backend/providers/serpapi-provider.js
const axios = require('axios');
const config = require('../config.json');

/**
 * Mock provider for SerpApi (Google Flights).
 *
 * @param {object} searchParams - The flight search parameters (origin, destination, date).
 * @param {object} country - The country configuration object.
 * @returns {Promise<Array<object>>} A promise that resolves to an array of flight results.
 */
async function search(searchParams, country) {
  console.log(`[SerpApi] Searching for flights from ${country.name} with params:`, searchParams);

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

  // In a real implementation, you would use axios to make a request to the SerpApi endpoint:
  // const response = await axios.get('https://serpapi.com/search', { ...axiosConfig, params: { ... } });
  // For now, we will just simulate the request and return mock data.

  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

  // Return realistic, hard-coded sample data
  return [
    {
      provider: 'SerpApi (Google Flights)',
      origin: searchParams.origin,
      destination: searchParams.destination,
      date: searchParams.date,
      price: {
        amount: Math.floor(400 + Math.random() * 200),
        currency: 'USD',
      },
      bookingLink: `https://www.google.com/flights#flt=${searchParams.origin}.${searchParams.destination}.${searchParams.date}`
    }
  ];
}

module.exports = {
  search
};
