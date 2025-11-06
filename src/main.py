import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.config.app_config import ConfigManager
from src.utils.logger import setup_logger, QtLogHandler
from src.automation.data_provider import DataProvider
from src.automation.web_provider import HeadlessWebProvider
from src.automation.stub_provider import StubProvider
from src.automation.slot_manager import BookingSlot

def get_provider(config: ConfigManager, slot_id: int) -> DataProvider:
    """Instantiates and returns the correct data provider based on config."""
    provider_name = config.get("PROVIDER", "StubProvider")

    if provider_name == "HeadlessWebProvider":
        profile_path = f"slots/{slot_id}"
        return HeadlessWebProvider(user_profile_path=profile_path)

    # Default to StubProvider for safety and testing
    return StubProvider()

def main():
    """Main application entry point."""
    logger = setup_logger()
    config_manager = ConfigManager()

    app = QApplication(sys.argv)

    # For now, let's assume we are running slot 1
    # In the full app, the GUI would manage this
    provider = get_provider(config_manager, 1)

    # --- Authentication (Simplified for now) ---
    # In a real scenario, you'd load the encrypted secret
    # and pass it to a login dialog.

    main_window = MainWindow(config_manager=config_manager)

    # Connect logger to GUI
    qt_log_handler = QtLogHandler()
    logger.addHandler(qt_log_handler)
    qt_log_handler.log_updated.connect(main_window.log)

    main_window.show()
    logger.info("Application started.")
    logger.info(f"Using provider: {provider.__class__.__name__}")

    # --- Example of starting a booking slot (will be triggered by a button) ---
    # This is a placeholder to show how the pieces connect.
    def start_test_booking():
        dummy_user = {"username": "test", "password": "pwd"}
        dummy_ticket = {"from": "A", "to": "B", "date": "01/01/2026"}

        # Note: We should manage the thread object to avoid it being garbage collected
        main_window.booking_thread = BookingSlot(1, provider, dummy_user, dummy_ticket)
        main_window.booking_thread.log_message.connect(logger.info)
        main_window.booking_thread.start()

    # In the real app, this would be a button click. We'll start it for demonstration.
    # main_window.some_button.clicked.connect(start_test_booking)
    # For now, let's just run the stub provider test
    if isinstance(provider, StubProvider):
        start_test_booking()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
