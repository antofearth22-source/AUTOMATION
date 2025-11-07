from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QTabWidget,
    QTableWidget, QHeaderView, QTableWidgetItem, QDialog, QHBoxLayout
)
from PySide6.QtCore import Slot
from src.security.credential_store import CredentialStore
from .account_dialog import AccountDialog

class AccountsTab(QWidget):
    """A widget to manage IRCTC account slots."""
    def __init__(self, store: CredentialStore, parent=None):
        super().__init__(parent)
        self.store = store

        layout = QVBoxLayout(self)

        self.account_table = QTableWidget()
        self.account_table.setColumnCount(5)
        self.account_table.setHorizontalHeaderLabels(["Label", "User ID", "Default", "Last Updated", "Actions"])
        header = self.account_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.account_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.add_account_button = QPushButton("Add New Account")
        self.add_account_button.clicked.connect(self.open_add_account_dialog)

        layout.addWidget(self.account_table)
        layout.addWidget(self.add_account_button)

        self.setLayout(layout)
        self.refresh_accounts()

    def refresh_accounts(self):
        """Reloads the account list from the store and populates the table."""
        self.account_table.setRowCount(0)
        slots = self.store.list_slots()
        default_slot = self.store.get_default_slot()

        for row, slot in enumerate(slots):
            self.account_table.insertRow(row)
            self.account_table.setItem(row, 0, QTableWidgetItem(slot["label"]))
            self.account_table.setItem(row, 1, QTableWidgetItem(slot["irctc_userid"]))

            default_text = "Yes" if default_slot and default_slot["slot_id"] == slot["slot_id"] else ""
            self.account_table.setItem(row, 2, QTableWidgetItem(default_text))

            self.account_table.setItem(row, 3, QTableWidgetItem(slot["updated_utc"]))

            self._add_action_buttons(row, slot["slot_id"])

    def _add_action_buttons(self, row: int, slot_id: str):
        """Helper to create and add the action buttons to a table row."""
        buttons_widget = QWidget()
        layout = QHBoxLayout(buttons_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.open_edit_account_dialog(slot_id))

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_account(slot_id))

        default_button = QPushButton("Make Default")
        default_button.clicked.connect(lambda: self.set_as_default(slot_id))

        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addWidget(default_button)

        self.account_table.setCellWidget(row, 4, buttons_widget)

    @Slot(str)
    def open_edit_account_dialog(self, slot_id: str):
        """Opens a dialog to edit an existing account slot."""
        slot_to_edit = next((s for s in self.store.list_slots() if s["slot_id"] == slot_id), None)
        if not slot_to_edit:
            QMessageBox.critical(self, "Error", "Could not find the selected slot.")
            return

        dialog = AccountDialog(slot_data=slot_to_edit, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.store.update_slot(
                    slot_id,
                    label=data["label"],
                    irctc_userid=data["irctc_userid"],
                    password=data["password"] or None, # Pass None if empty
                    totp_secret=data["totp_secret"] or None
                )
                QMessageBox.information(self, "Success", "Account slot has been updated.")
                self.refresh_accounts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update slot: {e}")

    @Slot(str)
    def delete_account(self, slot_id: str):
        """Deletes the specified account slot after confirmation."""
        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this account slot?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.store.delete_slot(slot_id)
                self.refresh_accounts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete slot: {e}")

    @Slot(str)
    def set_as_default(self, slot_id: str):
        """Sets the specified account as the default."""
        try:
            self.store.set_default_slot(slot_id)
            self.refresh_accounts()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set default slot: {e}")

    def open_add_account_dialog(self):
        """Opens a dialog to add a new account slot."""
        dialog = AccountDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["label"] or not data["irctc_userid"] or not data["password"]:
                QMessageBox.warning(self, "Input Error", "Label, User ID, and Password are required.")
                return

            try:
                self.store.create_slot(
                    label=data["label"],
                    irctc_userid=data["irctc_userid"],
                    password=data["password"],
                    totp_secret=data["totp_secret"] or None
                )
                QMessageBox.information(self, "Success", "New account slot has been created.")
                self.refresh_accounts()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create slot: {e}")


class SettingsTab(QWidget):
    # ... (rest of the class is unchanged)
    def __init__(self, config_manager, credential_store: CredentialStore, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.store = credential_store
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        self.general_tab = QWidget()
        self.accounts_tab = AccountsTab(self.store)
        self.provider_tab = QWidget()
        self.captcha_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.accounts_tab, "Accounts")
        self.tabs.addTab(self.provider_tab, "Provider")
        self.tabs.addTab(self.captcha_tab, "Captcha")

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        pass

    def save_all_settings(self):
        QMessageBox.information(self, "Settings", "Settings saved.")
