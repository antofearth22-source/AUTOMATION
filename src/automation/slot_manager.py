import time
from PySide6.QtCore import QThread, Signal
from src.automation.data_provider import DataProvider
from typing import Dict, Any

class BookingSlot(QThread):
    """
    Represents a single, threaded booking slot that runs a DataProvider
    to perform the booking workflow.
    """
    log_message = Signal(str)
    booking_status = Signal(str)

    def __init__(self, slot_id: int, provider: DataProvider, user_config: Dict[str, Any], ticket_config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.slot_id = slot_id
        self.provider = provider
        self.user_config = user_config
        self.ticket_config = ticket_config

    def run(self):
        """The main entry point for the thread's execution."""
        self.log_message.emit(f"Slot {self.slot_id}: Starting booking process...")
        self.booking_status.emit("Initializing")

        try:
            # Step 1: Login
            self.booking_status.emit("Logging In")
            login_success = self.provider.login(
                self.user_config['username'],
                self.user_config['password'],
                lambda: self._get_captcha_from_user() # This will need a GUI prompt
            )

            if not login_success:
                raise RuntimeError("Login failed. Check credentials or CAPTCHA.")

            # Step 2: Plan Journey
            self.booking_status.emit("Planning Journey")
            self.provider.plan_journey(
                self.ticket_config['from_station'],
                self.ticket_config['to_station'],
                self.ticket_config['date']
            )

            # Step 3: Get Trains and select one (simplified)
            self.booking_status.emit("Selecting Train")
            trains = self.provider.get_trains({})
            if not trains:
                raise RuntimeError("No trains found for the selected route.")

            selected_train = trains[0] # Simplification: just select the first train

            # Step 4: Book Ticket
            self.booking_status.emit("Booking Ticket")
            result = self.provider.book_ticket(
                selected_train,
                self.ticket_config['passengers'],
                lambda: self._handle_payment_from_user() # GUI prompt for payment
            )

            if result.get("status") == "CONFIRMED":
                self.log_message.emit(f"Slot {self.slot_id}: Booking SUCCESSFUL! PNR: {result.get('pnr')}")
                self.booking_status.emit("Success")
            else:
                raise RuntimeError(f"Booking failed. Status: {result.get('status')}")

        except Exception as e:
            self.log_message.emit(f"Slot {self.slot_id}: An error occurred: {e}")
            self.booking_status.emit("Failed")
        finally:
            self.provider.close()
            self.log_message.emit(f"Slot {self.slot_id}: Process finished.")

    def _get_captcha_from_user(self) -> str:
        """Placeholder for a GUI prompt to get the CAPTCHA solution."""
        self.log_message.emit("CAPTCHA required. Please solve it.")
        # In a real GUI, this would pop a dialog and wait.
        # For testing, we'll just return a dummy value.
        time.sleep(5) # Simulate user thinking time
        return "12345"

    def _handle_payment_from_user(self):
        """Placeholder for a GUI prompt to handle payment."""
        self.log_message.emit("Payment required. Please complete it in the browser.")
        # This would wait for a signal from the GUI that payment is complete.
        time.sleep(10) # Simulate user payment time

    def stop(self):
        """Stops the thread gracefully."""
        self.log_message.emit(f"Slot {self.slot_id}: Stopping thread...")
        self.requestInterruption()
        self.wait()
