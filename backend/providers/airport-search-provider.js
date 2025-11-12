// backend/providers/airport-search-provider.js
const { makeRequest } = require('../services/request-manager');
const config = require('../config.json');

/**
 * Mock provider for airport search.
 *
 * @param {string} query - The search query.
 * @returns {Promise<Array<object>>} A promise that resolves to an array of airport results.
 */
async function search(query) {
  console.log(`[AirportSearch] Searching for airports with query:`, query);

  // In a real implementation, you would use the request manager to make a request to an airport search API:
  // const axiosConfig = { ... };
  // const response = await makeRequest(axiosConfig);
  // For now, we will just simulate the request and return mock data.

  const mockAirports = [
    { name: 'London Heathrow (LHR)', code: 'LHR' },
    { name: 'London Gatwick (LGW)', code: 'LGW' },
    { name: 'London Stansted (STN)', code: 'STN' },
    { name: 'New York (JFK)', code: 'JFK' },
    { name: 'New York (LGA)', code: 'LGA' },
    { name: 'Tokyo (NRT)', code: 'NRT' },
    { name: 'Tokyo (HND)', code: 'HND' }
  ];

  const results = mockAirports.filter(airport =>
    airport.name.toLowerCase().includes(query.toLowerCase())
  );

  return Promise.resolve(results);
}

module.exports = {
  search
};
