import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from src.prox.models.base_models import Settings

class DriverFactory:
    """Creates and configures Selenium WebDriver instances."""

    @staticmethod
    def create_driver(settings: Settings) -> webdriver.Remote:
        """
        Creates a WebDriver instance based on the preferred browser in settings.
        """
        if settings.preferred_browser == "chrome":
            return DriverFactory._create_chrome_driver(settings)
        elif settings.preferred_browser == "edge":
            return DriverFactory._create_edge_driver(settings)
        elif settings.preferred_browser == "brave":
            return DriverFactory._create_brave_driver(settings)
        else:
            raise ValueError(f"Unsupported browser: {settings.preferred_browser}")

    @staticmethod
    def _create_chrome_driver(settings: Settings) -> webdriver.Chrome:
        """Creates a Chrome WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        service_path = ChromeDriverManager().install()
        service = ChromeService(executable_path=service_path)
        return webdriver.Chrome(service=service, options=options)

    @staticmethod
    def _create_edge_driver(settings: Settings) -> webdriver.Edge:
        """Creates an Edge WebDriver."""
        options = EdgeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        service_path = EdgeChromiumDriverManager().install()
        service = EdgeService(executable_path=service_path)
        return webdriver.Edge(service=service, options=options)

    @staticmethod
    def _create_brave_driver(settings: Settings) -> webdriver.Edge:
        """Creates a Brave WebDriver using the Edge driver."""
        options = EdgeOptions()
        if not settings.brave_path or not os.path.exists(settings.brave_path):
            raise FileNotFoundError("Brave browser path is not configured or invalid in settings.")
        options.binary_location = settings.brave_path

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        service_path = EdgeChromiumDriverManager().install()
        service = EdgeService(executable_path=service_path)
        return webdriver.Edge(service=service, options=options)
