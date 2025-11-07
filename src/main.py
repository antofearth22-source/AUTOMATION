import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.config.app_config import ConfigManager
from src.utils.logger import setup_logger, QtLogHandler
from src.automation.data_provider import DataProvider
from src.automation.web_provider import HeadlessWebProvider
from src.automation.stub_provider import StubProvider
from src.automation.slot_manager import BookingSlot
from src.security.credential_store import CredentialStore

class Application:
    def __init__(self):
        self.logger = setup_logger()
        self.config_manager = ConfigManager()
        self.credential_store = CredentialStore()
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(
            config_manager=self.config_manager,
            credential_store=self.credential_store
        )

        self._connect_signals()

        self.booking_threads = {}

    def _connect_signals(self):
        """Connects GUI signals to application logic."""
        self.main_window.new_ticket_tab.start_booking_button.clicked.connect(self.start_booking)

        qt_log_handler = QtLogHandler()
        self.logger.addHandler(qt_log_handler)
        qt_log_handler.log_updated.connect(self.main_window.log)

    def get_provider(self, slot_id: int) -> DataProvider:
        """Instantiates and returns the correct data provider."""
        provider_name = self.config_manager.get("PROVIDER", "StubProvider")
        if provider_name == "HeadlessWebProvider":
            profile_path = f"slots/{slot_id}"
            return HeadlessWebProvider(user_profile_path=profile_path, config=self.config_manager)
        return StubProvider()

    def start_booking(self):
        """Starts the booking process using the selected account and a saved ticket."""
        # 1. Get the active account
        active_slot_index = self.main_window.account_switcher.currentIndex()
        if active_slot_index == -1:
            QMessageBox.warning(self.main_window, "Error", "Please select an active account slot.")
            return
        slot_id = self.main_window.account_switcher.itemData(active_slot_index)

        try:
            credentials = self.credential_store.get_credentials(slot_id)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Could not retrieve credentials: {e}")
            return

        # 2. Get the ticket to book (for now, use the first saved ticket)
        saved_tickets = self.config_manager.load_user_data("saved_tickets.json").get("tickets", [])
        if not saved_tickets:
            QMessageBox.warning(self.main_window, "Error", "No saved tickets found. Please save a ticket configuration first.")
            return
        ticket_to_book = saved_tickets[0]

        # 3. Start the booking thread
        booking_slot_num = ticket_to_book.get("slot_number", 1)
        if booking_slot_num in self.booking_threads and self.booking_threads[booking_slot_num].isRunning():
            self.logger.warning(f"Slot {booking_slot_num} is already busy.")
            return

        provider = self.get_provider(booking_slot_num)

        thread = BookingSlot(booking_slot_num, provider, credentials, ticket_to_book)
        thread.log_message.connect(self.logger.info)
        thread.booking_status.connect(lambda status: self.main_window.status_bar.showMessage(f"Slot {booking_slot_num}: {status}"))

        self.booking_threads[booking_slot_num] = thread
        thread.start()
        self.logger.info(f"Booking process started for Slot {booking_slot_num} with account '{credentials['userid']}'.")

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = Application()
    app.run()
