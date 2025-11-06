from playwright.sync_api import sync_playwright, Page, Browser
from typing import Dict, Any, List, Callable, Optional
import time
import random

from src.automation.data_provider import DataProvider

class HeadlessWebProvider(DataProvider):
    """
    A DataProvider that interacts with the IRCTC website using Playwright.
    """
    def __init__(self, user_profile_path: str, slow_mo: int = 100):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.user_profile_path = user_profile_path
        self.slow_mo = slow_mo
        self.playwright = sync_playwright().start()

    def _launch_browser(self):
        """Launches a persistent Chromium browser."""
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_profile_path,
            headless=False, # Must be visible for compliance
            args=['--start-maximized'],
            slow_mo=self.slow_mo
        )
        self.page = self.browser.pages[0]
        self.page.set_default_timeout(60000)

    def _human_like_typing(self, selector: str, text: str):
        """Types text into an element with human-like delays."""
        if not self.page:
            return
        self.page.click(selector)
        self.page.fill(selector, "")
        for char in text:
            time.sleep(random.uniform(0.05, 0.15))
            self.page.type(selector, char)

    def login(self, username: str, password: str, captcha_callback: Callable[[], str]) -> bool:
        if not self.browser or not self.page:
            self._launch_browser()

        if not self.page:
            raise ConnectionError("Failed to launch browser page.")

        self.page.goto("https://www.irctc.co.in/nget/train-search")
        self.page.click("a[aria-label='Click here to Login']")

        self._human_like_typing("input[formcontrolname='userid']", username)
        self._human_like_typing("input[formcontrolname='password']", password)

        captcha_solution = captcha_callback()
        self._human_like_typing("input[formcontrolname='nlpAnswer']", captcha_solution)

        self.page.click("button.search_btn[type='submit']")

        try:
            self.page.wait_for_selector("a[aria-label='LOGOUT']", timeout=15000)
            return True
        except Exception:
            return False

    def plan_journey(self, from_station: str, to_station: str, date_str: str):
        # Implementation to be added in the next steps
        pass

    def get_trains(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implementation to be added in the next steps
        return []

    def book_ticket(self, train: Dict[str, Any], passengers: List[Dict[str, Any]], payment_callback) -> Dict[str, str]:
        # Implementation to be added in the next steps
        return {}

    def close(self):
        if self.browser:
            self.browser.close()
        self.playwright.stop()

if __name__ == '__main__':
    # This provider is meant to be instantiated and used by the SlotManager, not run directly.
    print("HeadlessWebProvider class defined.")
