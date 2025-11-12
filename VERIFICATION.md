# Manual End-to-End Verification Guide

This guide provides a step-by-step process for manually testing the complete functionality of the Geo-Variant Flight Fare Finder extension.

## Part 1: Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Start the backend server:**
    ```bash
    node index.js
    ```

    You should see output indicating that the server is running on port 3000.

## Part 2: Frontend Setup (Loading the Extension)

**Important:** To avoid errors, please use the provided `production.zip` file.

1.  **Find and Unzip:**
    *   In the root of the project, locate the file named `production.zip`.
    *   Unzip or extract this file. This will create a new folder named `production`.

2.  **Load the Extension in Chrome:**
    *   Open Google Chrome.
    *   Navigate to `chrome://extensions`.
    *   Enable **"Developer mode"** using the toggle in the top-right corner.
    *   Click the **"Load unpacked"** button.
    *   Select the **`production` folder** that you just unzipped.

3.  The "Geo-Variant Flight Fare Finder" extension should now appear in your list of extensions, ready for testing.

## Part 3: End-to-End Testing

1.  **Open the Extension:**
    *   Click the puzzle piece icon in the Chrome toolbar to open the extensions menu.
    *   Click on "Geo-Variant Flight Fare Finder" to open the popup.

2.  **Perform a Flight Search:**
    *   **Origin:** Enter `JFK`
    *   **Destination:** Enter `LHR`
    *   **Date:** Select a date in the future (e.g., 2025-12-25)
    *   **Date Flexibility:** Set to `1`
    *   **Stops:** Select "Non-stop only"
    *   Click "Search Flights".

3.  **Verify the Results:**
    *   You should see a "Searching for flights..." message, followed by a list of flight results.
    *   Verify that the results are sorted from cheapest to most expensive.
    *   Verify that each result displays the country name, the price in the local currency, and the price in USD.
    *   **Verify that all the flights in the results list have 0 stops.**

4.  **Test the "Booking Key" (Fingerprint Spoofing):**
    *   Find a result from a country other than your own (e.g., "Book from India").
    *   Click the "Book Now" button.

5.  **Verify the Proxy Warning:**
    *   A new tab should open with a "Proxy Warning".
    *   Read the warning and click "Proceed".

6.  **Verify the Spoofed Booking Tab:**
    *   A new tab should open with the booking link.
    *   To verify that the spoofing is working, you can open the developer tools (`Ctrl+Shift+I` or `Cmd+Opt+I`) and check the following:
        *   **IP Address:** The IP address should be different from your own. You can verify this by searching "what is my ip" in a separate, non-proxied tab and comparing it to the IP address in the proxied tab.
        *   **Accept-Language Header:** In the "Network" tab of the developer tools, select the main request and look at the "Request Headers". The `Accept-Language` header should match the language of the country you selected (e.g., `en-IN` for India).
        *   **Timezone and Language:** In the "Console" tab of the developer tools, enter the following commands:
            *   `new Intl.DateTimeFormat().resolvedOptions().timeZone` - This should return the timezone of the selected country (e.g., `Asia/Kolkata`).
            *   `navigator.language` - This should return the language of the selected country (e.g., `en-IN`).

7.  **Verify the Automatic Cleanup:**
    *   Close the booking tab.
    *   The proxy should now be disabled. You can verify this by trying to browse to a new website in a different tab. Your browsing should now be back to normal.

If all of these steps work as expected, the extension is working correctly.
