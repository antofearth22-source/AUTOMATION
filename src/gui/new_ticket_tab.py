from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QGroupBox, QHBoxLayout, QCompleter, QMessageBox
)
from PySide6.QtCore import QDate, Qt
import json
import uuid
from typing import Callable, List, Dict

class NewTicketTab(QWidget):
    def __init__(self, config_manager, resource_path_fn: Callable, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.resource_path = resource_path_fn

        # --- Load Station Data ---
        self.station_list = self.load_stations()
        station_names = [f"{s['name']} - {s['code']}" for s in self.station_list]

        self.main_layout = QVBoxLayout(self)

        # --- Journey Details ---
        journey_group = QGroupBox("Journey Details")
        journey_layout = QFormLayout()

        self.ticket_name_input = QLineEdit()
        self.ticket_name_input.setPlaceholderText("e.g., Delhi-Mumbai Business Trip")

        self.from_station_input = QLineEdit()
        self.to_station_input = QLineEdit()

        completer = QCompleter(station_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.from_station_input.setCompleter(completer)
        self.to_station_input.setCompleter(completer)

        self.journey_date_input = QDateEdit()
        self.journey_date_input.setCalendarPopup(True)
        self.journey_date_input.setDate(QDate.currentDate().addDays(1))
        self.journey_date_input.setMinimumDate(QDate.currentDate())

        self.class_input = QComboBox()
        self.class_input.addItems(["AC 3 Tier (3A)", "AC 2 Tier (2A)", "Sleeper (SL)", "AC Chair car (CC)"])

        journey_layout.addRow("Ticket Name:", self.ticket_name_input)
        journey_layout.addRow("From Station:", self.from_station_input)
        journey_layout.addRow("To Station:", self.to_station_input)
        journey_layout.addRow("Journey Date:", self.journey_date_input)
        journey_layout.addRow("Class:", self.class_input)
        journey_group.setLayout(journey_layout)
        self.main_layout.addWidget(journey_group)

        # --- Passenger Details ---
        passenger_group = QGroupBox("Passenger Details")
        self.passenger_layout = QVBoxLayout()
        self.passenger_forms: List[Dict[str, QWidget]] = []
        self.add_passenger_form() # Add one form by default
        passenger_group.setLayout(self.passenger_layout)
        self.main_layout.addWidget(passenger_group)

        # --- Add Passenger Button ---
        self.add_passenger_button = QPushButton("Add Another Passenger")
        self.add_passenger_button.clicked.connect(self.add_passenger_form)
        self.main_layout.addWidget(self.add_passenger_button)

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
        self.main_layout.addWidget(options_group)

        # --- Action Buttons ---
        action_layout = QHBoxLayout()
        self.save_ticket_button = QPushButton("Save Ticket Configuration")
        self.save_ticket_button.clicked.connect(self.save_ticket)
        self.start_booking_button = QPushButton("Start Booking") # This button will be connected in main.py

        action_layout.addStretch()
        action_layout.addWidget(self.save_ticket_button)
        action_layout.addWidget(self.start_booking_button)
        self.main_layout.addLayout(action_layout)

        self.setLayout(self.main_layout)

    def add_passenger_form(self):
        if len(self.passenger_forms) >= 4:
            QMessageBox.warning(self, "Limit Reached", "You can add a maximum of 4 passengers.")
            return

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
        self.passenger_forms.append({'widget': passenger_form, 'name': name, 'age': age, 'gender': gender})

    def load_stations(self):
        """Loads station data from the JSON file using the resource_path helper."""
        station_file = self.resource_path('data', 'stationlist.json')
        if not station_file.exists():
            QMessageBox.critical(self, "Error", f"Station list not found at {station_file}")
            return []
        try:
            with open(station_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('stations', [])
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", f"Could not decode JSON from {station_file}")
            return []

    def _extract_station_code(self, station_string: str) -> str:
        """Extracts the station code (e.g., 'NDLS') from a string like 'NEW DELHI - NDLS'."""
        if '-' in station_string:
            return station_string.split('-')[-1].strip()
        return "" # Return empty if format is unexpected

    def save_ticket(self):
        """Collects data from the form and saves it as a new ticket configuration."""
        # --- Validation ---
        if not self.ticket_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Ticket Name cannot be empty.")
            return

        from_station_code = self._extract_station_code(self.from_station_input.text())
        to_station_code = self._extract_station_code(self.to_station_input.text())

        if not from_station_code or not to_station_code:
            QMessageBox.warning(self, "Validation Error", "Please select valid 'From' and 'To' stations from the autocomplete list.")
            return

        # --- Data Collection ---
        ticket_data = {
            "id": f"ticket_{uuid.uuid4().hex[:8]}",
            "name": self.ticket_name_input.text().strip(),
            "from_station": from_station_code,
            "to_station": to_station_code,
            "journey_date": self.journey_date_input.date().toString("yyyy-MM-dd"),
            "class": self.class_input.currentText().split(" (")[1][:-1], # Extracts '3A' from 'AC 3 Tier (3A)'
            "quota": "Tatkal",
            "passengers": [],
            "payment_method": self.payment_method_input.currentText(),
            "slot_number": int(self.slot_input.currentText().split(" ")[1])
        }

        for p_form in self.passenger_forms:
            name = p_form['name'].text().strip()
            age = p_form['age'].text().strip()
            if not name or not age:
                QMessageBox.warning(self, "Validation Error", "All passenger name and age fields must be filled.")
                return

            ticket_data["passengers"].append({
                "name": name,
                "age": int(age),
                "gender": p_form['gender'].currentText()
            })

        if not ticket_data["passengers"]:
            QMessageBox.warning(self, "Validation Error", "At least one passenger is required.")
            return

        # --- Saving the data ---
        try:
            saved_tickets = self.config_manager.load_user_data("saved_tickets.json")
            saved_tickets.setdefault("tickets", []).append(ticket_data)
            self.config_manager.save_user_data("saved_tickets.json", saved_tickets)
            QMessageBox.information(self, "Success", "Ticket configuration has been saved successfully!")
            self._clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save ticket configuration: {e}")

    def _clear_form(self):
        """Resets the form to its default state after saving."""
        self.ticket_name_input.clear()
        self.from_station_input.clear()
        self.to_station_input.clear()
        self.journey_date_input.setDate(QDate.currentDate().addDays(1))
        self.class_input.setCurrentIndex(0)

        # Remove all but the first passenger form
        for i in range(len(self.passenger_forms) - 1, 0, -1):
            form_to_remove = self.passenger_forms.pop(i)
            form_to_remove['widget'].deleteLater()

        # Clear the first passenger form
        if self.passenger_forms:
            self.passenger_forms[0]['name'].clear()
            self.passenger_forms[0]['age'].clear()
            self.passenger_forms[0]['gender'].setCurrentIndex(0)

        self.payment_method_input.setCurrentIndex(0)
        self.slot_input.setCurrentIndex(0)
