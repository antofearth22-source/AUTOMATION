// frontend/warning.js

document.addEventListener('DOMContentLoaded', () => {
  const proceedButton = document.getElementById('proceed-button');
  const cancelButton = document.getElementById('cancel-button');

  proceedButton.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'proceedWithBooking' });
  });

  cancelButton.addEventListener('click', () => {
    window.close();
  });
});
