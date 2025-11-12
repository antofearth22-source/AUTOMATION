const fs = require('fs');
const path = require('path');
const express = require('express');
const pLimit = require('p-limit').default;
const currencyConverter = require('./services/currency-converter');

// Load configuration
const config = JSON.parse(fs.readFileSync('config.json', 'utf-8'));

// Dynamically load providers
const providers = [];
const providersDir = path.join(__dirname, 'providers');
fs.readdirSync(providersDir).forEach(file => {
  if (file.endsWith('.js')) {
    const provider = require(path.join(providersDir, file));
    providers.push(provider);
    console.log(`Loaded provider: ${file}`);
  }
});

/**
 * The core aggregation engine.
 */
async function searchAll(searchParams, dateFlexibility = 0) {
  const limit = pLimit(5);
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
 * Normalizes and sorts the flight results.
 */
async function normalizeAndSort(flights) {
  const normalizedFlights = [];
  const targetCurrency = 'USD';

  for (const flight of flights) {
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

// --- API Endpoint ---
app.post('/search-flights', apiKeyMiddleware, async (req, res) => {
  const { origin, destination, date, date_flexibility } = req.body;

  if (!origin || !destination || !date) {
    return res.status(400).json({ error: 'Missing required search parameters' });
  }

  try {
    const searchParams = { origin, destination, date };
    console.log(`[API] Received search request:`, searchParams, `with flexibility: ${date_flexibility || 0}`);

    const allFlights = await searchAll(searchParams, date_flexibility);
    const sortedFlights = await normalizeAndSort(allFlights);

    res.json(sortedFlights);
  } catch (error) {
    console.error('Error during flight search:', error);
    res.status(500).json({ error: 'An internal server error occurred' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
