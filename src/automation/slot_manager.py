from PySide6.QtCore import QThread, Signal
from src.automation.irctc_bot import IRCTC_Bot
import os

class BookingSlot(QThread):
    """
    Represents a single, threaded booking slot that runs an IRCTC bot
    in an isolated browser profile.
    """
    # Signals to communicate with the GUI
    log_message = Signal(str)
    booking_status = Signal(str) # e.g., "Success", "Failed", "In Progress"

    def __init__(self, slot_id: int, user_config: dict, ticket_config: dict, parent=None):
        super().__init__(parent)
        self.slot_id = slot_id
        self.user_config = user_config
        self.ticket_config = ticket_config

        self.profile_path = os.path.join(os.getcwd(), f'slots/{self.slot_id}')
        self.bot = None

    def run(self):
        """The main entry point for the thread's execution."""
        self.log_message.emit(f"Slot {self.slot_id}: Initializing...")

        try:
            self.bot = IRCTC_Bot(user_profile_path=self.profile_path)
            self.bot.launch_browser()
            self.log_message.emit(f"Slot {self.slot_id}: Browser launched.")

            # This is a placeholder for the full booking workflow
            # In the final version, this will call the login, plan_journey, etc.
            self.booking_status.emit("In Progress")

            # --- Placeholder Workflow ---
            # 1. Login
            # 2. Plan Journey
            # 3. Select Train
            # 4. Fill Passenger Details
            # 5. Make Payment
            # 6. Get PNR

            self.log_message.emit(f"Slot {self.slot_id}: Automation logic would run here.")

            self.booking_status.emit("Completed") # Or "Failed"

        except Exception as e:
            self.log_message.emit(f"Slot {self.slot_id}: An error occurred: {e}")
            self.booking_status.emit("Failed")
        finally:
            if self.bot:
                self.bot.close_browser()
            self.log_message.emit(f"Slot {self.slot_id}: Process finished.")

    def stop(self):
        """Stops the thread gracefully."""
        self.log_message.emit(f"Slot {self.slot_id}: Stopping thread...")
        self.requestInterruption()
        self.wait() # Wait for the thread to finish


if __name__ == '__main__':
    # This test demonstrates how to use the BookingSlot thread.
    # It cannot be run in this environment but serves as a structural example.
    print("BookingSlot class is defined for managing concurrent booking threads.")
    print("This script is intended to be integrated into the main GUI application.")
