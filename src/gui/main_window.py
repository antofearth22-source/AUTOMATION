import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QTextEdit, QStatusBar, QPushButton
)
from PySide6.QtCore import QTimer
from datetime import datetime
from src.gui.new_ticket_tab import NewTicketTab
from src.gui.saved_tickets_tab import SavedTicketsTab
from src.gui.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
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
        self.new_ticket_tab = NewTicketTab()
        self.saved_tickets_tab = SavedTicketsTab()
        self.settings_tab = SettingsTab(config_manager=self.config_manager)

        self.tabs.addTab(self.new_ticket_tab, "New Ticket")
        self.tabs.addTab(self.saved_tickets_tab, "Saved Tickets")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.main_layout.addWidget(self.tabs)

        # --- Bottom Section: Log Console ---
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #f0f0f0; font-family: Consolas, monospace;")
        self.main_layout.addWidget(self.log_console)

        # --- Action Buttons ---
        self.start_booking_button = QPushButton("Start Booking")
        self.main_layout.addWidget(self.start_booking_button)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to start.")

        # --- Timer for the clock ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000) # Update every second
        self.update_clock()

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
        def get(self, key, default=None):
            return default

    app = QApplication(sys.argv)
    window = MainWindow(config_manager=MockConfigManager())
    window.show()

    # Example of logging
    window.log("Application started.")
    window.log("This is a test message for the log console.")

    sys.exit(app.exec())
