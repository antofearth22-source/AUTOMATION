from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QMessageBox
from src.config.app_config import ConfigManager
from src.security.credential_manager import CredentialManager

class SettingsTab(QWidget):
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.layout = QVBoxLayout(self)

        # --- IRCTC Account Management (Placeholder) ---
        accounts_group = QGroupBox("IRCTC Accounts")
        accounts_layout = QFormLayout()
        # ... (implementation for this section will be done later)
        accounts_group.setLayout(accounts_layout)
        self.layout.addWidget(accounts_group)

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
        self.layout.addWidget(totp_group)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def save_totp_secret(self):
        """
        Encrypts and saves the new TOTP secret to the app configuration.
        """
        secret = self.totp_secret_input.text()
        if not secret:
            QMessageBox.warning(self, "Input Error", "TOTP Secret cannot be empty.")
            return

        try:
            # Encrypt the secret using DPAPI
            encrypted_secret = CredentialManager.encrypt_data(secret)

            # Load, update, and save the app config
            app_config = self.config_manager.load_config('app_config')
            app_config['totp_secret'] = encrypted_secret
            self.config_manager.save_config('app_config', app_config)

            self.totp_secret_input.clear()
            QMessageBox.information(self, "Success", "TOTP secret has been saved securely.")

        except Exception as e:
            # This will happen on non-Windows systems
            QMessageBox.critical(self, "Error", f"Could not save the secret: {e}\n\nThis feature requires a Windows environment.")
