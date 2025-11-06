from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QGroupBox, QHBoxLayout, QCompleter
)
from PySide6.QtCore import QDate
import json
import os

class NewTicketTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Load Station Data ---
        self.station_list = self.load_stations()
        station_names = [f"{s['name']} - {s['code']}" for s in self.station_list]

        self.layout = QVBoxLayout(self)

        # --- Journey Details ---
        journey_group = QGroupBox("Journey Details")
        journey_layout = QFormLayout()

        self.from_station_input = QLineEdit()
        self.to_station_input = QLineEdit()

        # Autocomplete for station inputs
        completer = QCompleter(station_names)
        completer.setCaseSensitivity(False) # Case-insensitive matching
        self.from_station_input.setCompleter(completer)
        self.to_station_input.setCompleter(completer)

        self.journey_date_input = QDateEdit()
        self.journey_date_input.setCalendarPopup(True)
        self.journey_date_input.setDate(QDate.currentDate().addDays(1))
        self.journey_date_input.setMinimumDate(QDate.currentDate())

        self.class_input = QComboBox()
        self.class_input.addItems(["AC 3 Tier (3A)", "AC 2 Tier (2A)", "Sleeper (SL)", "AC Chair car (CC)"])

        journey_layout.addRow("From Station:", self.from_station_input)
        journey_layout.addRow("To Station:", self.to_station_input)
        journey_layout.addRow("Journey Date:", self.journey_date_input)
        journey_layout.addRow("Class:", self.class_input)
        journey_group.setLayout(journey_layout)
        self.layout.addWidget(journey_group)

        # --- Passenger Details ---
        passenger_group = QGroupBox("Passenger Details")
        self.passenger_layout = QVBoxLayout()
        # We will dynamically add passenger forms here
        self.add_passenger_form() # Add one form by default
        passenger_group.setLayout(self.passenger_layout)
        self.layout.addWidget(passenger_group)

        # --- Payment and Options ---
        options_group = QGroupBox("Options")
        options_layout = QFormLayout()
        self.payment_method_input = QComboBox()
        self.payment_method_input.addItems(["UPI", "Credit/Debit Card"])
        self.slot_input = QComboBox()
        self.slot_input.addItems(["Slot 1", "Slot 2", "Slot 3"])
        options_layout.addRow("Payment Method:", self.payment_method_input)
        options_layout.addRow("Assign to Slot:", self.slot_input)
        options_group.setLayout(options_layout)
        self.layout.addWidget(options_group)

        # --- Action Buttons ---
        self.save_ticket_button = QPushButton("Save Ticket Configuration")
        self.layout.addWidget(self.save_ticket_button)

        self.setLayout(self.layout)

    def add_passenger_form(self):
        passenger_form = QWidget()
        form_layout = QHBoxLayout(passenger_form)

        name = QLineEdit()
        name.setPlaceholderText("Name")
        age = QLineEdit()
        age.setPlaceholderText("Age")
        age.setMaxLength(3)
        gender = QComboBox()
        gender.addItems(["Male", "Female", "Other"])

        form_layout.addWidget(name)
        form_layout.addWidget(age)
        form_layout.addWidget(gender)

        self.passenger_layout.addWidget(passenger_form)

    def load_stations(self):
        """Loads station data from the JSON file."""
        # This assumes the script is run from the project root
        station_file = 'data/stationlist.json'
        if not os.path.exists(station_file):
            print(f"Warning: {station_file} not found.")
            return []
        try:
            with open(station_file, 'r') as f:
                data = json.load(f)
            return data.get('stations', [])
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {station_file}.")
            return []


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("New Ticket Tab - Test")
    window.setCentralWidget(NewTicketTab())
    window.setGeometry(100, 100, 600, 500)
    window.show()
    sys.exit(app.exec())
