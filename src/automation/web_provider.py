from playwright.sync_api import sync_playwright, Page, Browser
from typing import Dict, Any, List, Callable, Optional
import time
import random
import tempfile
import logging
from pathlib import Path

from src.automation.data_provider import DataProvider
from src.automation.captcha_gateway import CaptchaGateway
from src.config.app_config import ConfigManager

logger = logging.getLogger(__name__)

class HeadlessWebProvider(DataProvider):
    """
    A DataProvider that interacts with the IRCTC website using Playwright.
    """
    def __init__(self, user_profile_path: str, config: ConfigManager, slow_mo: int = 100):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.captcha_gateway: Optional[CaptchaGateway] = None
        self.user_profile_path = user_profile_path
        self.slow_mo = slow_mo
        self.playwright = sync_playwright().start()
        self.config = config

        # Initialize the CAPTCHA gateway
        captcha_solver_path = self.config.get("CAPTCHA_SOLVER_PATH")
        try:
            self.captcha_gateway = CaptchaGateway(captcha_solver_path)
            logger.info("CaptchaGateway initialized successfully.")
        except FileNotFoundError as e:
            logger.error(f"Failed to initialize CaptchaGateway: {e}")
            self.captcha_gateway = None

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

        # --- CAPTCHA Solving Logic ---
        captcha_solution = ""
        if self.captcha_gateway:
            try:
                # Find the CAPTCHA image element and save it
                captcha_element = self.page.locator("img.captcha-img").first

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    captcha_path = tmp_file.name
                    captcha_element.screenshot(path=captcha_path)

                logger.info(f"CAPTCHA image saved to {captcha_path}")

                # Call the external solver
                result = self.captcha_gateway.solve(captcha_path)

                if result.get("ok"):
                    captcha_solution = result.get("text", "")
                    logger.info(f"CAPTCHA solved successfully: {captcha_solution}")
                else:
                    logger.error(f"CAPTCHA solving failed: {result.get('error')}")
                    # Fallback to manual input if automatic solving fails
                    captcha_solution = captcha_callback()

                # Clean up the temporary file
                Path(captcha_path).unlink()

            except Exception:
                logger.exception("An error occurred during automated CAPTCHA solving. Falling back to manual.")
                captcha_solution = captcha_callback()
        else:
            logger.warning("CaptchaGateway not available. Falling back to manual CAPTCHA input.")
            captcha_solution = captcha_callback()
        # --- End CAPTCHA Logic ---

        self._human_like_typing("input[formcontrolname='nlpAnswer']", captcha_solution)
        self.page.click("button.search_btn[type='submit']")

        try:
            self.page.wait_for_selector("a[aria-label='LOGOUT']", timeout=15000)
            return True
        except Exception:
            return False

    def plan_journey(self, from_station: str, to_station: str, date_str: str):
        pass

    def get_trains(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    def book_ticket(self, train: Dict[str, Any], passengers: List[Dict[str, Any]], payment_callback) -> Dict[str, str]:
        return {}

    def close(self):
        if self.browser:
            self.browser.close()
        self.playwright.stop()
