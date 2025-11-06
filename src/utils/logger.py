import logging
import os
from datetime import datetime
from PySide6.QtCore import QObject, Signal
import sys

# This allows the script to be run directly for testing by adding the project root to the path.
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.paths import resource_path

class QtLogHandler(logging.Handler, QObject):
    """A custom logging handler that emits a Qt signal for each log record."""
    log_updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__()
        QObject.__init__(self, parent)

    def emit(self, record):
        msg = self.format(record)
        self.log_updated.emit(msg)

def setup_logger():
    """Configures and returns a logger with file and GUI handlers."""
    # Ensure the log directory exists in a user-writable location
    log_dir_base = os.getenv('LOCALAPPDATA', resource_path())
    log_dir = os.path.join(log_dir_base, 'IrctcPro', 'logs')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("IRCTC_Pro")
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - (%(threadName)s) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # --- File Handler ---
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"session_{session_timestamp}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- Console Handler (for debugging in dev environment) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logger configured. Log file: {log_file}")
    return logger

if __name__ == '__main__':
    # Test the logger configuration
    logger = setup_logger()
    logger.info("This is a test log message.")
    print("\nLog test complete.")
    # The output will show the log path, which will include 'localappdata' on Windows.
    # In this environment, it will fall back to the project's root.
