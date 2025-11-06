from playwright.sync_api import sync_playwright, Page, Browser
import time
import random
from typing import Optional

def human_like_typing(page: Page, selector: str, text: str):
    """Types text into an element with human-like delays."""
    page.click(selector)
    page.fill(selector, "") # Clear the field first
    for char in text:
        time.sleep(random.uniform(0.05, 0.15)) # 50-150ms delay
        page.type(selector, char)

class IRCTC_Bot:
    def __init__(self, user_profile_path: str):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.user_profile_path = user_profile_path
        self.playwright = sync_playwright().start()

    def launch_browser(self):
        """Launches a persistent Chromium browser."""
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_profile_path,
            headless=False,
            args=['--start-maximized']
        )
        self.page = self.browser.pages[0]
        self.page.set_default_timeout(60000)

    def login(self, username, password, captcha_callback):
        """Handles the entire login process."""
        print("Starting login process...")
        self.page.goto("https://www.irctc.co.in/nget/train-search")
        self.page.click("a[aria-label='Click here to Login']")

        # Use stable formcontrolname selectors
        human_like_typing(self.page, "input[formcontrolname='userid']", username)
        human_like_typing(self.page, "input[formcontrolname='password']", password)

        print("Please solve the CAPTCHA in the browser window.")
        captcha_solution = captcha_callback()
        human_like_typing(self.page, "input[formcontrolname='nlpAnswer']", captcha_solution)

        self.page.click("button.search_btn[type='submit']")

        try:
            self.page.wait_for_selector("a[aria-label='LOGOUT']", timeout=10000)
            print("Login successful.")
            return True
        except Exception:
            print("Login failed. Please check credentials or CAPTCHA.")
            return False

    def plan_journey(self, from_station, to_station, date_str):
        """Fills out the 'Plan My Journey' form."""
        print("Planning journey...")
        # Use more robust selectors based on formcontrolname
        from_input_selector = "input[aria-labelledby='p-highlight-0']"
        human_like_typing(self.page, from_input_selector, from_station)
        self.page.keyboard.press("Enter")

        to_input_selector = "input[aria-labelledby='p-highlight-1']"
        human_like_typing(self.page, to_input_selector, to_station)
        self.page.keyboard.press("Enter")

        # Date handling can be brittle, directly setting the value is more reliable
        date_selector = "input[formcontrolname='jDate']"
        self.page.evaluate(f"document.querySelector('{date_selector}').value = '{date_str}'")
        self.page.keyboard.press("Enter")

        self.page.click("button.train_Search[type='submit']")
        print("Journey form submitted.")

    def close_browser(self):
        if self.browser:
            self.browser.close()
        self.playwright.stop()

if __name__ == '__main__':
    print("IRCTC_Bot class is defined with improved selectors.")
    print("This script is intended to be integrated into the main application.")
