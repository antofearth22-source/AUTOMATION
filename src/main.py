import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.config.app_config import ConfigManager
from src.utils.logger import setup_logger, QtLogHandler
from src.automation.data_provider import DataProvider
from src.automation.web_provider import HeadlessWebProvider
from src.automation.stub_provider import StubProvider
from src.automation.slot_manager import BookingSlot

class Application:
    def __init__(self):
        self.logger = setup_logger()
        self.config_manager = ConfigManager()
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(config_manager=self.config_manager)

        self._connect_signals()

        # This will hold references to running threads
        self.booking_threads = {}

    def _connect_signals(self):
        """Connects GUI signals to application logic."""
        self.main_window.start_booking_button.clicked.connect(self.start_booking)

        # Connect logger to GUI
        qt_log_handler = QtLogHandler()
        self.logger.addHandler(qt_log_handler)
        qt_log_handler.log_updated.connect(self.main_window.log)

    def get_provider(self, slot_id: int) -> DataProvider:
        """Instantiates and returns the correct data provider based on config."""
        provider_name = self.config_manager.get("PROVIDER", "StubProvider")
        if provider_name == "HeadlessWebProvider":
            profile_path = f"slots/{slot_id}"
            return HeadlessWebProvider(user_profile_path=profile_path)
        return StubProvider()

    def start_booking(self):
        """Starts the booking process for a configured slot."""
        # For this example, we'll just start a booking on slot 1
        slot_id = 1

        if slot_id in self.booking_threads and self.booking_threads[slot_id].isRunning():
            self.logger.warning(f"Slot {slot_id} is already busy.")
            return

        provider = self.get_provider(slot_id)

        # In a real scenario, these would be loaded from the GUI forms
        dummy_user = {"username": "test", "password": "pwd"}
        dummy_ticket = {"from": "NDLS", "to": "BCT", "date": "01/01/2026"}

        thread = BookingSlot(slot_id, provider, dummy_user, dummy_ticket)
        thread.log_message.connect(self.logger.info)
        thread.booking_status.connect(lambda status: self.main_window.status_bar.showMessage(f"Slot {slot_id}: {status}"))

        self.booking_threads[slot_id] = thread
        thread.start()
        self.logger.info(f"Booking process started for Slot {slot_id} using {provider.__class__.__name__}.")

    def run(self):
        """Shows the main window and starts the application event loop."""
        self.main_window.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = Application()
    app.run()
