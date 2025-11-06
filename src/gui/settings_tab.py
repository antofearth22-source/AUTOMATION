from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox
from src.config.app_config import ConfigManager
from src.security.credential_manager import CredentialManager

class SettingsTab(QWidget):
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager
        layout = QVBoxLayout(self)

        # --- Provider Settings ---
        provider_group = QGroupBox("Data Provider")
        provider_layout = QFormLayout()
        self.provider_select = QComboBox()
        self.provider_select.addItems(["HeadlessWebProvider", "StubProvider"])
        provider_layout.addRow("Provider:", self.provider_select)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)

        # --- IRCTC Account Management ---
        accounts_group = QGroupBox("IRCTC Accounts")
        accounts_layout = QFormLayout()
        self.user_id_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        accounts_layout.addRow("IRCTC User ID:", self.user_id_input)
        accounts_layout.addRow("Password:", self.password_input)
        self.save_account_button = QPushButton("Add/Update Account")
        accounts_layout.addWidget(self.save_account_button)
        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)

        # --- TOTP Secret Configuration ---
        totp_group = QGroupBox("TOTP Authentication")
        totp_layout = QFormLayout()
        self.totp_secret_input = QLineEdit()
        self.totp_secret_input.setPlaceholderText("Enter your Base32 secret key")
        totp_layout.addRow("Secret Key:", self.totp_secret_input)
        self.save_totp_button = QPushButton("Save TOTP Secret")
        self.save_totp_button.clicked.connect(self.save_totp_secret)
        totp_layout.addWidget(self.save_totp_button)
        totp_group.setLayout(totp_layout)
        layout.addWidget(totp_group)

        # --- Main Save Button ---
        self.save_settings_button = QPushButton("Save All Settings")
        self.save_settings_button.clicked.connect(self.save_all_settings)
        layout.addWidget(self.save_settings_button)

        layout.addStretch()
        self.setLayout(layout)

        self.load_settings()

    def load_settings(self):
        """Loads current settings and populates the fields."""
        provider = self.config_manager.get('PROVIDER', 'HeadlessWebProvider')
        self.provider_select.setCurrentText(provider)

    def save_all_settings(self):
        """Saves all settings from this tab."""
        # This will save the configuration to a json file.
        # For now, it just shows a message.
        selected_provider = self.provider_select.currentText()
        QMessageBox.information(self, "Settings", f"Provider set to '{selected_provider}'.\nPlease restart the application for changes to take effect.")

    def save_totp_secret(self):
        """Encrypts and saves the new TOTP secret."""
        secret = self.totp_secret_input.text()
        if not secret:
            QMessageBox.warning(self, "Input Error", "TOTP Secret cannot be empty.")
            return

        try:
            CredentialManager.save_secret("totp_secret", secret)
            self.totp_secret_input.clear()
            QMessageBox.information(self, "Success", "TOTP secret has been saved securely.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save the secret: {e}")
