// backend/services/request-manager.js
const axios = require('axios');

/**
 * Makes a request with automatic retries.
 *
 * @param {object} axiosConfig - The axios configuration for the request.
 * @param {number} retries - The number of times to retry the request.
 * @returns {Promise<object>} The response data.
 */
async function makeRequest(axiosConfig, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await axios(axiosConfig);
      return response.data;
    } catch (error) {
      console.log(`[RequestManager] Request failed (attempt ${i + 1}/${retries}):`, error.message);
      if (i === retries - 1) {
        throw error;
      }
    }
  }
}

module.exports = {
  makeRequest
};
