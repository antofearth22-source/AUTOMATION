from PySide6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
)
from src.security.totp_auth import TotpManager

class LoginDialog(QDialog):
    def __init__(self, totp_secret: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IRCTC Pro - Authentication")
        self.setModal(True)

        self.totp_secret = totp_secret

        self.layout = QVBoxLayout()

        self.info_label = QLabel("Enter your 6-digit authentication code:")
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(6)
        self.code_input.setPlaceholderText("_ _ _ _ _ _")

        self.login_button = QPushButton("Login")

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.code_input)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

        self.login_button.clicked.connect(self.handle_login)
        self.code_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        code = self.code_input.text()
        if not code.isdigit() or len(code) != 6:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid 6-digit code.")
            return

        totp_manager = TotpManager()
        if totp_manager.verify_code(self.totp_secret, code):
            self.accept()  # Close the dialog and signal success
        else:
            QMessageBox.critical(self, "Authentication Failed", "The code is incorrect. Please try again.")
            self.code_input.clear()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    import pyotp # For generating a test secret

    # This is a dummy QApplication to test the dialog
    app = QApplication(sys.argv)

    # In the real application, the secret would be loaded from an encrypted file.
    # For this test, we'll generate one.
    test_secret = pyotp.random_base32()

    dialog = LoginDialog()
    dialog.totp_secret = test_secret

    # To make testing easier, we'll print the current valid code to the console.
    print(f"Auth Secret: {test_secret}")
    print(f"Current Valid Code: {pyotp.TOTP(test_secret).now()}")

    dialog.show()

    # The application will exit when the dialog is closed.
    # If the login is successful, the dialog's result will be QDialog.Accepted.
    if dialog.exec() == QDialog.Accepted:
        print("SUCCESS: Login successful!")
    else:
        print("INFO: Login failed or dialog was closed.")

    sys.exit()
