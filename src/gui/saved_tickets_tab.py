from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QHeaderView, QTableWidgetItem, QPushButton
)
from PySide6.QtCore import Slot
from src.config.app_config import ConfigManager

class SavedTicketsTab(QWidget):
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager

        self.main_layout = QVBoxLayout(self)

        self.ticket_table = QTableWidget()
        self.ticket_table.setColumnCount(7)
        self.ticket_table.setHorizontalHeaderLabels(["Name", "Route", "Date", "Class", "Quota", "Slot", "Actions"])
        header = self.ticket_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ticket_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.refresh_tickets)

        self.main_layout.addWidget(self.ticket_table)
        self.main_layout.addWidget(self.refresh_button)

        self.setLayout(self.main_layout)
        self.refresh_tickets()

    @Slot()
    def refresh_tickets(self):
        """Reloads the saved tickets and populates the table."""
        self.ticket_table.setRowCount(0)
        saved_data = self.config_manager.load_user_data("saved_tickets.json")
        tickets = saved_data.get("tickets", [])

        for row, ticket in enumerate(tickets):
            self.ticket_table.insertRow(row)
            self.ticket_table.setItem(row, 0, QTableWidgetItem(ticket.get("name", "")))
            route = f"{ticket.get('from_station', '')} -> {ticket.get('to_station', '')}"
            self.ticket_table.setItem(row, 1, QTableWidgetItem(route))
            self.ticket_table.setItem(row, 2, QTableWidgetItem(ticket.get("journey_date", "")))
            self.ticket_table.setItem(row, 3, QTableWidgetItem(ticket.get("class", "")))
            self.ticket_table.setItem(row, 4, QTableWidgetItem(ticket.get("quota", "General"))) # Default to General if not found
            self.ticket_table.setItem(row, 5, QTableWidgetItem(str(ticket.get("slot_number", ""))))

            # Placeholder for action buttons
            self.ticket_table.setCellWidget(row, 6, QPushButton("Use as Template"))
