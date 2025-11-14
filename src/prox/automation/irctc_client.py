# Main IRCTC automation client using Selenium.

import logging
import time
import random
import tempfile
import os
from typing import Optional, Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from src.prox.models.base_models import Settings, IRCTCAccount, TicketTemplate
from src.prox.automation.driver_factory import DriverFactory
from src.prox.automation import selectors
from src.prox.services.captcha_solver import TrueCaptchaService

# --- Custom Exceptions ---
class LoginFailedError(Exception):
    """Raised when login does not succeed within the timeout."""
    pass

class JourneySearchError(Exception):
    """Raised when there's an issue on the journey planning page."""
    pass

class PassengerFormError(Exception):
    """Raised when there's an issue on the passenger details page."""
    pass

class PaymentPageError(Exception):
    """Raised when the payment page cannot be reached."""
    pass


class IrctcClient:
    """
    Orchestrates the IRCTC booking workflow using Selenium.
    """
    def __init__(self, settings: Settings, logger: logging.Logger, status_callback: Optional[Callable[[str], None]] = None):
        self.settings = settings
        self.logger = logger
        self.status_callback = status_callback
        self.driver: Optional[WebDriver] = None

    def _update_status(self, message: str):
        """Logs a message and sends it to the UI callback if available."""
        self.logger.info(message)
        if self.status_callback:
            self.status_callback(message)

    def _human_type(self, element, text: str):
        """Types text into an element with a human-like delay."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def open_browser(self):
        """Launches the browser based on application settings."""
        self._update_status("Opening browser...")
        self.driver = DriverFactory.create_driver(self.settings)
        self.driver.maximize_window()
        self._update_status("Browser opened successfully.")

    def close(self):
        """Closes the browser if it's running."""
        if self.driver:
            self._update_status("Closing browser.")
            self.driver.quit()
            self.driver = None

    def login(self, account: IRCTCAccount):
        """
        Navigates to the login page, fills credentials, and handles CAPTCHA.
        Implements a hybrid CAPTCHA approach: tries automatic solving first,
        then falls back to manual user input.
        """
        if not self.driver:
            raise RuntimeError("Browser is not open. Call open_browser() first.")

        self._update_status(f"Navigating to login page for user '{account.username}'...")
        self.driver.get("https://www.irctc.co.in/nget/train-search") # URL will redirect to login

        wait = WebDriverWait(self.driver, 10)

        # Close initial popup if it appears
        try:
            close_button = wait.until(EC.element_to_be_clickable(selectors.CommonSelectors.MODAL_CLOSE_BUTTON))
            close_button.click()
            self._update_status("Closed initial welcome popup.")
        except TimeoutException:
            self._update_status("No welcome popup appeared.")

        # Fill credentials
        username_input = wait.until(EC.presence_of_element_located(selectors.LoginPageSelectors.USERNAME_INPUT))
        password_input = wait.until(EC.presence_of_element_located(selectors.LoginPageSelectors.PASSWORD_INPUT))

        self._human_type(username_input, account.username)
        self._human_type(password_input, account.password)

        # Hybrid CAPTCHA handling
        time.sleep(3) # Wait 3 seconds as requested

        captcha_service = TrueCaptchaService(
            api_key=self.settings.truecaptcha_api_key,
            user_id=self.settings.truecaptcha_user_id,
            logger=self.logger
        )
        captcha_image = wait.until(EC.presence_of_element_located(selectors.LoginPageSelectors.CAPTCHA_IMAGE))

        # Use a temporary file for the captcha image
        solved_text = None
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            captcha_path = temp_file.name

        try:
            captcha_image.screenshot(captcha_path)
            solved_text = captcha_service.solve_from_image_path(captcha_path)
        finally:
            # Clean up the temporary file
            if os.path.exists(captcha_path):
                os.remove(captcha_path)

        if solved_text:
            self._update_status("CAPTCHA solved automatically. Entering text.")
            captcha_input = wait.until(EC.presence_of_element_located(selectors.LoginPageSelectors.CAPTCHA_INPUT))
            self._human_type(captcha_input, solved_text)
            wait.until(EC.element_to_be_clickable(selectors.LoginPageSelectors.LOGIN_BUTTON)).click()
        else:
            self._update_status("Automatic CAPTCHA failed. Please solve the CAPTCHA and click 'SIGN IN' in the browser.")

        # Wait for manual or automatic login to complete
        try:
            self._update_status("Waiting for login success...")
            wait = WebDriverWait(self.driver, 120) # 120-second timeout for user
            wait.until(EC.presence_of_element_located(selectors.LoginPageSelectors.LOGOUT_BUTTON))
            self._update_status("Login successful.")
        except TimeoutException:
            raise LoginFailedError("Login did not complete within the 120-second timeout.")

    def open_booking_page(self):
        # In this workflow, login redirects to the booking page, so this can be a simple pass-through.
        self._update_status("Already on booking page.")

    def apply_template(self, template: TicketTemplate):
        """
        Fills the journey and passenger details based on the ticket template.
        """
        self._update_status("Applying ticket template...")
        wait = WebDriverWait(self.driver, 10)

        try:
            # --- Fill Journey Details ---
            self._update_status("Filling journey details...")
            from_station_input = wait.until(EC.presence_of_element_located(selectors.JourneyPageSelectors.FROM_STATION_INPUT))
            to_station_input = wait.until(EC.presence_of_element_located(selectors.JourneyPageSelectors.TO_STATION_INPUT))

            self._human_type(from_station_input, template.journey.from_station)
            time.sleep(0.5) # Wait for autocomplete
            from_station_input.send_keys(Keys.ENTER)
            self._human_type(to_station_input, template.journey.to_station)
            time.sleep(0.5) # Wait for autocomplete
            to_station_input.send_keys(Keys.ENTER)

            # --- Handle Date Selection ---
            target_date = template.journey.journey_date
            target_month = target_date.strftime("%B").upper()
            target_year = str(target_date.year)
            target_day = str(target_date.day)

            date_picker = wait.until(EC.element_to_be_clickable(selectors.JourneyPageSelectors.JOURNEY_DATE_PICKER))
            date_picker.click()

            # Navigate months until the target month and year are visible
            for _ in range(12): # Max 12 clicks to prevent infinite loops
                month_year_display = wait.until(EC.presence_of_element_located(selectors.JourneyPageSelectors.CALENDAR_MONTH_YEAR_DISPLAY)).text
                if target_month in month_year_display.upper() and target_year in month_year_display:
                    self._update_status(f"Found target month/year: {month_year_display}")
                    break

                wait.until(EC.element_to_be_clickable(selectors.JourneyPageSelectors.CALENDAR_NEXT_MONTH_BUTTON)).click()
            else:
                raise JourneySearchError(f"Could not find month {target_month} {target_year} in the calendar after 12 attempts.")

            # Click the target day
            day_selector = (
                selectors.JourneyPageSelectors.CALENDAR_DAY_CELL[0],
                selectors.JourneyPageSelectors.CALENDAR_DAY_CELL[1].format(day=target_day)
            )
            day_element = wait.until(EC.element_to_be_clickable(day_selector))
            day_element.click()
            self._update_status(f"Selected date {target_date.strftime('%Y-%m-%d')}.")

            # --- Handle Dropdowns ---
            Select(wait.until(EC.presence_of_element_located(selectors.JourneyPageSelectors.CLASS_DROPDOWN))).select_by_value(template.journey.class_code)
            Select(wait.until(EC.presence_of_element_located(selectors.JourneyPageSelectors.QUOTA_DROPDOWN))).select_by_value(template.journey.quota)

            search_button = wait.until(EC.element_to_be_clickable(selectors.JourneyPageSelectors.SEARCH_BUTTON))
            search_button.click()
            self._update_status("Train search initiated.")

            # --- Select Train and Book ---
            self._update_status(f"Searching for train '{template.journey.train_name}'...")
            train_row_selector = (
                selectors.TrainListPageSelectors.TRAIN_AVAILABILITY_ROW[0],
                selectors.TrainListPageSelectors.TRAIN_AVAILABILITY_ROW[1].format(train_name=template.journey.train_name)
            )
            train_row = wait.until(EC.presence_of_element_located(train_row_selector))
            book_now_button = train_row.find_element(*selectors.TrainListPageSelectors.BOOK_NOW_BUTTON)
            book_now_button.click()
            self._update_status("Found train and clicked 'Book Now'.")

        except TimeoutException as e:
            raise JourneySearchError(f"Failed to find or interact with journey search elements: {e}")

        try:
            # --- Fill Passenger Details ---
            self._update_status("Filling passenger details...")

            # Find all input elements first, as they are not uniquely identifiable
            name_inputs = wait.until(EC.presence_of_all_elements_located(selectors.PassengerFormPageSelectors.PASSENGER_NAME_INPUT))
            age_inputs = self.driver.find_elements(*selectors.PassengerFormPageSelectors.PASSENGER_AGE_INPUT)
            gender_selects = self.driver.find_elements(*selectors.PassengerFormPageSelectors.PASSENGER_GENDER_SELECT)
            berth_selects = self.driver.find_elements(*selectors.PassengerFormPageSelectors.PASSENGER_BERTH_SELECT)

            for i, passenger in enumerate(template.passengers):
                if i >= len(name_inputs):
                    self._update_status(f"Warning: More passengers in template than available input fields on page. Stopping at passenger {i+1}.")
                    break

                self._update_status(f"Filling details for passenger {i+1}: {passenger.name}")

                self._human_type(name_inputs[i], passenger.name)
                self._human_type(age_inputs[i], str(passenger.age))
                Select(gender_selects[i]).select_by_visible_text(passenger.gender)
                Select(berth_selects[i]).select_by_visible_text(passenger.berth)

            mobile_input = wait.until(EC.presence_of_element_located(selectors.PassengerFormPageSelectors.CONTACT_MOBILE_INPUT))
            self._human_type(mobile_input, template.mobile)
            self._update_status("All passenger details filled.")

        except TimeoutException as e:
            raise PassengerFormError(f"Failed to find or interact with passenger form elements: {e}")

    def go_to_payment(self, template: TicketTemplate):
        """
        Proceeds through the review screen and selects the payment mode.
        Stops once the payment gateway page is loaded.
        """
        self._update_status("Proceeding to payment page...")
        wait = WebDriverWait(self.driver, 10)

        try:
            # Click the main continue/submit button on the passenger page
            proceed_button = wait.until(EC.element_to_be_clickable(selectors.PassengerFormPageSelectors.PROCEED_TO_PAYMENT_BUTTON))
            proceed_button.click()
            self._update_status("Submitted passenger form.")

            # On the review page, click the final confirmation
            # Note: This might be the same selector as the previous page, or a new one.
            # Reusing for this placeholder.
            final_proceed_button = wait.until(EC.element_to_be_clickable(selectors.PassengerFormPageSelectors.PROCEED_TO_PAYMENT_BUTTON))
            final_proceed_button.click()
            self._update_status("Confirmed review, moving to payment selection.")

            # Select the payment mode
            self._update_status(f"Selecting payment mode: '{template.payment_mode_label}'")
            payment_radio_selector = (
                selectors.PaymentPageSelectors.PAYMENT_MODE_RADIO[0],
                selectors.PaymentPageSelectors.PAYMENT_MODE_RADIO[1].format(payment_mode=template.payment_mode_label)
            )
            payment_radio = wait.until(EC.element_to_be_clickable(payment_radio_selector))
            payment_radio.click()

            pay_and_book_button = wait.until(EC.element_to_be_clickable(selectors.PaymentPageSelectors.PAY_AND_BOOK_BUTTON))
            pay_and_book_button.click()
            self._update_status("Submitted payment choice.")

            # Wait for the final payment gateway to load
            wait_long = WebDriverWait(self.driver, 30)
            wait_long.until(EC.presence_of_element_located(selectors.PaymentPageSelectors.PAYMENT_GATEWAY_IFRAME))
            self._update_status("Successfully reached payment gateway. Handing over to user.")

        except TimeoutException as e:
            raise PaymentPageError(f"Failed to navigate to the payment gateway: {e}")
