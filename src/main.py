import sys
from PySide6.QtWidgets import QApplication, QDialog
from src.gui.login_dialog import LoginDialog
from src.gui.main_window import MainWindow
from src.config.app_config import ConfigManager
from src.security.credential_manager import CredentialManager
from src.utils.logger import setup_logger, QtLogHandler

def main():
    """
    Main application entry point.
    """
    # 1. Setup Logger
    logger = setup_logger()

    # 2. Initialize Config Manager
    config_manager = ConfigManager()

    # 3. Load App Config
    app_config = config_manager.load_config('app_config')
    encrypted_secret = app_config.get("totp_secret")

    totp_secret = ""
    if encrypted_secret:
        try:
            totp_secret = CredentialManager.decrypt_data(encrypted_secret)
        except Exception as e:
            logger.error(f"Failed to decrypt TOTP secret: {e}. Please configure a new one in Settings.")

    # 4. Initialize Application
    app = QApplication(sys.argv)

    # 5. Show the login dialog first
    # If the secret is not set, the dialog will (and should) fail authentication
    login_dialog = LoginDialog(totp_secret=totp_secret)

    if login_dialog.exec() == QDialog.Accepted:
        # 6. If login is successful, show the main window
        main_window = MainWindow(config_manager=config_manager)

        # Connect the logger to the GUI
        qt_log_handler = QtLogHandler()
        logger.addHandler(qt_log_handler)
        qt_log_handler.log_updated.connect(main_window.log)

        main_window.show()
        logger.info("Authentication successful. Welcome!")
        sys.exit(app.exec())
    else:
        logger.info("Login failed or was cancelled. Exiting.")
        sys.exit(0)

if __name__ == '__main__':
    main()
