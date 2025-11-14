# This file centralizes all Selenium locators for the IRCTC website.
# By keeping them in one place, we can easily update them when the site changes.

from selenium.webdriver.common.by import By

# Using tuples: (By.<Strategy>, "<selector_string>")

class CommonSelectors:
    """Selectors for elements that may appear on multiple pages."""
    MODAL_POPUP = (By.XPATH, "//div[contains(@class, 'ui-dialog')]")
    MODAL_CLOSE_BUTTON = (By.XPATH, "//button[contains(text(), 'OK')]")

class LoginPageSelectors:
    """Selectors for the main IRCTC login page."""
    USERNAME_INPUT = (By.XPATH, "//input[@formcontrolname='userid']")
    PASSWORD_INPUT = (By.XPATH, "//input[@formcontrolname='password']")
    CAPTCHA_IMAGE = (By.ID, "captchaImg")
    CAPTCHA_INPUT = (By.ID, "captcha")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'SIGN IN')]")
    # Element to confirm successful login
    LOGOUT_BUTTON = (By.XPATH, "//a[contains(text(), 'Logout')]")

class JourneyPageSelectors:
    """Selectors for the 'Plan My Journey' page."""
    FROM_STATION_INPUT = (By.XPATH, "//input[contains(@aria-controls, 'pr_id_1_list')]")
    TO_STATION_INPUT = (By.XPATH, "//input[contains(@aria-controls, 'pr_id_2_list')]")
    JOURNEY_DATE_PICKER = (By.XPATH, "//input[contains(@class, 'ng-tns-c58-10')]")
    # --- Calendar Selectors ---
    CALENDAR_NEXT_MONTH_BUTTON = (By.XPATH, "//a[contains(@class, 'ui-datepicker-next')]")
    CALENDAR_MONTH_YEAR_DISPLAY = (By.XPATH, "//div[contains(@class, 'ui-datepicker-title')]")
    # This selector will be formatted with the day number
    CALENDAR_DAY_CELL = (By.XPATH, "//a[contains(@class, 'ui-state-default') and text()='{day}']")
    CLASS_DROPDOWN = (By.ID, "journeyClass")
    QUOTA_DROPDOWN = (By.ID, "journeyQuota")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(text(), 'Search')]")

class TrainListPageSelectors:
    """Selectors for the page that lists available trains."""
    TRAIN_AVAILABILITY_ROW = (By.XPATH, "//div[contains(normalize-space(), '{train_name}')]/ancestor::app-train-avl-enq")
    BOOK_NOW_BUTTON = (By.XPATH, ".//button[contains(text(), 'Book Now')]")
    FIRST_AVAILABLE_TRAIN_ROW = (By.XPATH, "(//app-train-avl-enq)[1]") # Fallback

class PassengerFormPageSelectors:
    """Selectors for the passenger details form."""
    PASSENGER_NAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='Passenger Name']")
    PASSENGER_AGE_INPUT = (By.CSS_SELECTOR, "input[placeholder='Age']")
    PASSENGER_GENDER_SELECT = (By.CSS_SELECTOR, "select.form-control") # This might need to be more specific
    PASSENGER_BERTH_SELECT = (By.CSS_SELECTOR, "select[formcontrolname='passengerBerthChoice']")
    CONTACT_MOBILE_INPUT = (By.ID, "mobileNumber")
    PROCEED_TO_PAYMENT_BUTTON = (By.XPATH, "//button[contains(text(), 'Continue')]")

class PaymentPageSelectors:
    """Selectors for the payment method selection page."""
    # This needs a dynamic selector based on the payment_mode_label from the template
    PAYMENT_MODE_RADIO = (By.XPATH, "//div[contains(normalize-space(), '{payment_mode}')]/ancestor::div[contains(@class, 'payment-type-box')]//div[@class='bank-type-radio']")
    PAY_AND_BOOK_BUTTON = (By.XPATH, "//button[contains(text(), 'Pay & Book')]")
    # Wait for any element that signifies the external gateway page, like a bank logo
    PAYMENT_GATEWAY_IFRAME = (By.XPATH, "//*[contains(text(), 'HDFC') or contains(text(), 'SBI') or contains(@id, 'upi-qr')]")
