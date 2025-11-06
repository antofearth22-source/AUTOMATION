import logging
import os
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class QtLogHandler(logging.Handler, QObject):
    """
    A custom logging handler that emits a Qt signal for each log record.
    This allows redirecting logs to a GUI widget.
    """
    log_updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__()
        QObject.__init__(self, parent)

    def emit(self, record):
        msg = self.format(record)
        self.log_updated.emit(msg)

def setup_logger(log_dir="logs"):
    """
    Configures and returns a logger with file and GUI handlers.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a logger
    logger = logging.getLogger("IRCTC_Pro")
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - (%(threadName)s) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # --- File Handler ---
    # Rotates logs, keeping the most recent.
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(os.path.join(log_dir, f"session_{session_timestamp}.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- GUI Handler (via Qt Signal) ---
    # The handler itself will be added in the main GUI window
    # so it can be connected to the log widget.

    # --- Console Handler (for debugging) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logger configured successfully.")
    return logger

if __name__ == '__main__':
    # Test the logger configuration
    import threading
    import time

    logger = setup_logger()
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

    def worker():
        thread_name = threading.current_thread().name
        logger.info(f"Logging from thread: {thread_name}")

    # Simulate logging from multiple threads (like our booking slots)
    thread1 = threading.Thread(target=worker, name="Slot-1")
    thread2 = threading.Thread(target=worker, name="Slot-2")
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    print("\nLog test complete. Check the 'logs' directory for the output file.")
