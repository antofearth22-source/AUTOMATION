const fs = require('fs');
const path = require('path');
const express = require('express');
const pLimit = require('p-limit');
const currencyConverter = require('./services/currency-converter');
const airportSearchProvider = require('./providers/airport-search-provider');

// Load configuration
const config = JSON.parse(fs.readFileSync('config.json', 'utf-8'));

// Dynamically load providers
const providers = [];
const providersDir = path.join(__dirname, 'providers');
fs.readdirSync(providersDir).forEach(file => {
  if (file.endsWith('.js') && file !== 'airport-search-provider.js') {
    const provider = require(path.join(providersDir, file));
    providers.push(provider);
    console.log(`Loaded provider: ${file}`);
  }
});

/**
 * The core aggregation engine.
 */
async function searchAll(searchParams, dateFlexibility = 0) {
  const limit = pLimit(config.concurrency);
  const promises = [];
  const baseDate = new Date(searchParams.date);

  for (let i = -dateFlexibility; i <= dateFlexibility; i++) {
    const searchDate = new Date(baseDate);
    searchDate.setDate(baseDate.getDate() + i);
    const dateString = searchDate.toISOString().split('T')[0];
    const newSearchParams = { ...searchParams, date: dateString };

    for (const country of config.countries) {
      for (const provider of providers) {
        promises.push(limit(() => provider.search(newSearchParams, country).then(results => {
          return results.map(result => ({ ...result, country }));
        })));
      }
    }
  }

  const resultsByProvider = await Promise.all(promises);
  return resultsByProvider.flat();
}

/**
 * Normalizes, sorts, and filters the flight results.
 */
async function processResults(flights, stopsFilter) {
  let filteredFlights = flights;

  // --- Filtering ---
  if (stopsFilter !== 'any') {
    const maxStops = parseInt(stopsFilter, 10);
    filteredFlights = flights.filter(flight => flight.stops <= maxStops);
  }

  // --- Normalization and Sorting ---
  const normalizedFlights = [];
  const targetCurrency = 'USD';

  for (const flight of filteredFlights) {
    const convertedAmount = await currencyConverter.convert(flight.price.amount, flight.price.currency, targetCurrency);
    normalizedFlights.push({
      ...flight,
      convertedPrice: {
        amount: convertedAmount,
        currency: targetCurrency
      }
    });
  }

  normalizedFlights.sort((a, b) => a.convertedPrice.amount - b.convertedPrice.amount);
  return normalizedFlights;
}

const app = express();
app.use(express.json());

// --- Security Middleware ---
const apiKeyMiddleware = (req, res, next) => {
  const apiKey = req.get('X-API-Key');
  if (apiKey && apiKey === config.apiKey) {
    next();
  } else {
    res.status(401).json({ error: 'Unauthorized: Invalid API Key' });
  }
};

// --- API Endpoints ---
app.post('/search-flights', apiKeyMiddleware, async (req, res) => {
  const { origin, destination, date, date_flexibility, stops } = req.body;

  if (!origin || !destination || !date) {
    return res.status(400).json({ error: 'Missing required search parameters' });
  }

  try {
    const searchParams = { origin, destination, date };
    console.log(`[API] Received search request:`, searchParams, `with flexibility: ${date_flexibility || 0}, stops: ${stops || 'any'}`);

    const allFlights = await searchAll(searchParams, date_flexibility);
    const processedFlights = await processResults(allFlights, stops);

    res.json(processedFlights);
  } catch (error) {
    console.error('Error during flight search:', error);
    res.status(500).json({ error: 'An internal server error occurred' });
  }
});

app.get('/autocomplete-airports', apiKeyMiddleware, async (req, res) => {
  const { query } = req.query;

  if (!query) {
    return res.status(400).json({ error: 'Missing required query parameter' });
  }

  try {
    const results = await airportSearchProvider.search(query);
    res.json(results);
  } catch (error) {
    console.error('Error during airport autocomplete:', error);
    res.status(500).json({ error: 'An internal server error occurred' });
  }
});


const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
}


module.exports = app;
