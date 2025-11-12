// frontend/render.test.js

/**
 * @jest-environment jsdom
 */

const { renderResults } = require('./popup.js');

describe('renderResults', () => {
  it('should correctly render a list of flights', () => {
    // Create a mock DOM element to render into
    const resultsDiv = document.createElement('div');

    const mockFlights = [
      {
        country: { name: 'United States' },
        price: { amount: 500, currency: 'USD' },
        convertedPrice: { amount: 500, currency: 'USD' },
        bookingLink: 'http://example.com/us'
      },
      {
        country: { name: 'United Kingdom' },
        price: { amount: 400, currency: 'GBP' },
        convertedPrice: { amount: 500, currency: 'USD' },
        bookingLink: 'http://example.com/uk'
      }
    ];

    renderResults(mockFlights, resultsDiv);

    expect(resultsDiv.children.length).toBe(2);
    expect(resultsDiv.querySelector('h3').textContent).toBe('Book from United States');
  });
});
