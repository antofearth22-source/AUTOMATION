// backend/services/currency-converter.js

const MOCK_RATES = {
  USD: 1.0,
  GBP: 1.25,
  EUR: 1.1,
  INR: 0.012,
  JPY: 0.0067,
  BRL: 0.19,
  ZAR: 0.053
};

/**
 * Converts an amount from a source currency to a target currency.
 *
 * @param {number} amount - The amount to convert.
 * @param {string} fromCurrency - The source currency code (e.g., 'GBP').
 * @param {string} toCurrency - The target currency code (e.g., 'USD').
 * @returns {Promise<number>} The converted amount.
 */
async function convert(amount, fromCurrency, toCurrency) {
  console.log(`[CurrencyConverter] Converting ${amount} ${fromCurrency} to ${toCurrency}`);

  const fromRate = MOCK_RATES[fromCurrency];
  const toRate = MOCK_RATES[toCurrency];

  if (!fromRate || !toRate) {
    throw new Error(`Unsupported currency. Conversion from ${fromCurrency} to ${toCurrency} is not available.`);
  }

  // Convert to base currency (USD) first, then to target currency
  const amountInUsd = amount * fromRate;
  const convertedAmount = amountInUsd / toRate;

  return Promise.resolve(parseFloat(convertedAmount.toFixed(2)));
}

module.exports = {
  convert
};
