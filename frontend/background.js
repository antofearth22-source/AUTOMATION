// frontend/background.js

console.log('Background service worker loaded.');

let bookingTabDetails = {};

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'bookFlight') {
    const { url, country } = message.payload;
    console.log(`[Background] Received booking request for`, country, `at ${url}`);

    chrome.tabs.create({ url: 'warning.html', active: true }, (tab) => {
      chrome.storage.local.set({ bookingData: { url, country, warningTabId: tab.id } });
    });

    return true;
  }
});

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === 'proceedWithBooking') {
    const { bookingData } = await chrome.storage.local.get('bookingData');
    if (bookingData) {
      await applySpoofingAndCreateTab(bookingData.url, bookingData.country);
      chrome.tabs.remove(bookingData.warningTabId);
    }
  }
});

async function applySpoofingAndCreateTab(url, country) {
  // --- 1. IP Spoofing (Proxy) ---
  const proxyConfig = {
    mode: 'fixed_servers',
    rules: {
      singleProxy: {
        scheme: 'http',
        host: `proxy.${country.code.toLowerCase()}.example.com`,
        port: 8080
      },
      bypassList: ["<local>"]
    }
  };

  await chrome.proxy.settings.set({ value: proxyConfig, scope: 'regular' });
  console.log(`[Proxy] Set proxy for ${country.name}`);

  // Create the booking tab
  chrome.tabs.create({ url: url, active: true }, (tab) => {
    const ruleId = tab.id + 1; // Use a tab-based ID for the rule
    bookingTabDetails[tab.id] = { ruleId };
    console.log(`[Background] Created tab with ID: ${tab.id}`);
    applySpoofingToTab(tab.id, country, ruleId);
  });
}

async function applySpoofingToTab(tabId, country, ruleId) {
  // --- 2. Header Spoofing (Accept-Language) ---
  const languageRule = {
    id: ruleId,
    priority: 1,
    action: {
      type: 'modifyHeaders',
      requestHeaders: [{
        header: 'Accept-Language',
        operation: 'set',
        value: country.language
      }]
    },
    condition: { tabIds: [tabId], resourceTypes: ['main_frame'] }
  };
  await chrome.declarativeNetRequest.updateSessionRules({ addRules: [languageRule] });
  console.log(`[DNR] Set Accept-Language to ${country.language} for tab ${tabId}`);

  // --- 3. Browser Spoofing (Timezone & Language) ---
  const scriptInjection = {
    target: { tabId: tabId },
    func: (timezone, language) => {
      Object.defineProperty(navigator, 'language', { get: () => language });
      Object.defineProperty(navigator, 'languages', { get: () => [language] });
      Intl.DateTimeFormat.prototype.resolvedOptions = new Proxy(Intl.DateTimeFormat.prototype.resolvedOptions, {
        apply: function(target, thisArg, argumentsList) {
          const result = Reflect.apply(target, thisArg, argumentsList);
          result.timeZone = timezone;
          return result;
        }
      });
    },
    args: [country.timezone, country.language],
    world: 'MAIN',
    injectImmediately: true
  };
  await chrome.scripting.executeScript(scriptInjection);
  console.log(`[Scripting] Injected script to spoof timezone to ${country.timezone} for tab ${tabId}`);
}

// --- Handle Proxy Authentication ---
chrome.webRequest.onAuthRequired.addListener(
  (details, callback) => {
    console.log('[Auth] Proxy authentication required.');
    callback({
      authCredentials: {
        username: 'placeholder-username',
        password: 'placeholder-password'
      }
    });
  },
  { urls: ["<all_urls>"] },
  ['asyncBlocking']
);

// --- Cleanup when the booking tab is closed ---
chrome.tabs.onRemoved.addListener(async (tabId) => {
  if (bookingTabDetails[tabId]) {
    await chrome.proxy.settings.clear({ scope: 'regular' });
    const { ruleId } = bookingTabDetails[tabId];
    delete bookingTabDetails[tabId];
    await chrome.declarativeNetRequest.updateSessionRules({ removeRuleIds: [ruleId] });
    console.log(`[Cleanup] Cleared proxy and spoofing rules for closed tab ${tabId}`);
  }
});
