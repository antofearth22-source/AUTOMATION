import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QTextEdit, QStatusBar, QHBoxLayout, QComboBox
)
from PySide6.QtCore import QTimer
from datetime import datetime

from src.gui.new_ticket_tab import NewTicketTab
from src.gui.saved_tickets_tab import SavedTicketsTab
from src.gui.settings_tab import SettingsTab
from src.utils.paths import resource_path

from src.security.credential_store import CredentialStore

class MainWindow(QMainWindow):
    def __init__(self, config_manager, credential_store: CredentialStore, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.credential_store = credential_store
        self.setWindowTitle("IRCTC Pro Tatkal Booking Assistant")
        self.setGeometry(100, 100, 1200, 800)

        # Main container widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Top Section: Clock and Status ---
        self.status_layout = QVBoxLayout()
        self.clock_label = QLabel()
        self.status_label = QLabel("Status: Ready | Success: 0 | Failed: 0 | Pending: 0")
        self.status_layout.addWidget(self.clock_label)
        self.status_layout.addWidget(self.status_label)
        self.main_layout.addLayout(self.status_layout)

        # --- Middle Section: Tabs ---
        self.tabs = QTabWidget()
        self.new_ticket_tab = NewTicketTab(config_manager=self.config_manager, resource_path_fn=resource_path)
        self.saved_tickets_tab = SavedTicketsTab(config_manager=self.config_manager)
        self.settings_tab = SettingsTab(config_manager=self.config_manager, credential_store=self.credential_store)

        self.tabs.addTab(self.new_ticket_tab, "New Ticket")
        self.tabs.addTab(self.saved_tickets_tab, "Saved Tickets")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.main_layout.addWidget(self.tabs)

        # --- Bottom Section: Log Console ---
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #f0f0f0; font-family: Consolas, monospace;")
        self.main_layout.addWidget(self.log_console)

        # --- Footer ---
        footer_layout = QHBoxLayout()
        self.account_switcher = QComboBox()
        self.account_switcher.setPlaceholderText("Select Account")
        footer_layout.addWidget(QLabel("Active Account:"))
        footer_layout.addWidget(self.account_switcher)
        footer_layout.addStretch()
        self.main_layout.addLayout(footer_layout)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to start.")

        # --- Timer for the clock ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000) # Update every second
        self.update_clock()

        # --- Populate Accounts & Connect Signals ---
        self._populate_accounts()
        self.account_switcher.currentIndexChanged.connect(self.on_account_switch)

    def _populate_accounts(self):
        """Clears and repopulates the account switcher combobox."""
        self.account_switcher.clear()
        slots = self.credential_store.list_slots()
        default_slot = self.credential_store.get_default_slot()

        for i, slot in enumerate(slots):
            display_text = f"{slot['label']} ({slot['irctc_userid']})"
            self.account_switcher.addItem(display_text, userData=slot['slot_id'])
            if default_slot and slot['slot_id'] == default_slot['slot_id']:
                self.account_switcher.setCurrentIndex(i)

    def on_account_switch(self, index: int):
        """Handles the logic for switching the active account."""
        if index == -1:
            return
        # slot_id = self.account_switcher.itemData(index) # This would be used to fetch account details
        self.clear_session()
        self.log(f"Switched to account slot: {self.account_switcher.currentText()}")

    def clear_session(self):
        """Placeholder for clearing session data like cookies and cached tokens."""
        self.log("Session data cleared for account switch.")

    def update_clock(self):
        now = datetime.now()
        self.clock_label.setText(f"<b>System Time:</b> {now.strftime('%Y-%m-%d %H:%M:%S')}")

    def log(self, message):
        """Appends a message to the log console."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_console.append(f"[{timestamp}] {message}")


if __name__ == '__main__':
    # This block is for testing the main window in isolation.
    class MockConfigManager:
        def get(self, key, default=None): return default

    class MockCredentialStore(CredentialStore):
        def __init__(self):
            # Bypass the real __init__ which touches the filesystem
            pass
        def list_slots(self): return []
        def get_default_slot(self): return None
        def set_default_slot(self, slot_id): pass
        def create_slot(self, label, irctc_userid, password, totp_secret=None): return "mock_id"
        def update_slot(self, slot_id, label=None, irctc_userid=None, password=None, totp_secret=None, notes=None): pass
        def delete_slot(self, slot_id): pass
        def get_credentials(self, slot_id): return {}

    app = QApplication(sys.argv)
    window = MainWindow(config_manager=MockConfigManager(), credential_store=MockCredentialStore())
    window.show()

    # Example of logging
    window.log("Application started.")
    window.log("This is a test message for the log console.")

    sys.exit(app.exec())
