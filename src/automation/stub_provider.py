from typing import Dict, Any, List, Callable
import time
import json
import sys
import os

# This allows the script to be run directly for testing.
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.automation.data_provider import DataProvider
from src.utils.paths import resource_path

class StubProvider(DataProvider):
    """
    A mock DataProvider for testing purposes. It returns canned data and
    simulates delays without making any real network requests.
    """
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        print("StubProvider initialized.")

    def login(self, username: str, password: str, captcha_callback: Callable[[], str]) -> bool:
        print(f"STUB: Simulating login for user '{username}'.")
        time.sleep(1) # Simulate network delay
        if self.should_succeed:
            print("STUB: Login successful.")
            return True
        else:
            print("STUB: Login failed.")
            return False

    def plan_journey(self, from_station: str, to_station: str, date_str: str):
        print(f"STUB: Simulating journey search from {from_station} to {to_station} on {date_str}.")
        time.sleep(1)

    def get_trains(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        print("STUB: Loading canned train data.")
        time.sleep(1)
        # Load sample train data from a test file
        test_data_path = resource_path('data', 'test', 'sample_trains.json')
        if test_data_path.exists():
            with open(test_data_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('trains', [])
        return []

    def book_ticket(self, train: Dict[str, Any], passengers: List[Dict[str, Any]], payment_callback: Callable) -> Dict[str, str]:
        print(f"STUB: Simulating booking ticket on train {train.get('number')}.")
        time.sleep(2)

        # Simulate user interaction for payment
        payment_callback()

        if self.should_succeed:
            print("STUB: Booking successful.")
            return {"pnr": "1234567890", "status": "CONFIRMED"}
        else:
            print("STUB: Booking failed.")
            return {"pnr": "", "status": "FAILED"}

    def close(self):
        print("STUB: Provider closed.")
        pass

if __name__ == '__main__':
    # This block allows for direct testing of the stub provider.
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.utils.paths import resource_path

    # Create dummy test data
    test_data_dir = resource_path('data', 'test')
    test_data_dir.mkdir(exist_ok=True)
    dummy_trains = {
        "trains": [
            {"name": "TEST EXPRESS", "number": "00001"},
            {"name": "STUB SUPERFAST", "number": "00002"}
        ]
    }
    with open(test_data_dir / 'sample_trains.json', 'w') as f:
        json.dump(dummy_trains, f)

    # --- Test StubProvider ---
    print("\n--- Testing StubProvider ---")
    provider = StubProvider(should_succeed=True)

    login_success = provider.login("testuser", "testpass", lambda: "12345")
    assert login_success

    trains = provider.get_trains({})
    assert len(trains) == 2
    print(f"STUB: Found trains: {trains}")

    booking_result = provider.book_ticket(trains[0], [], lambda: print("STUB: Simulating payment..."))
    assert booking_result['status'] == "CONFIRMED"

    provider.close()
    print("\nSUCCESS: StubProvider tests passed.")

    # Clean up
    (test_data_dir / 'sample_trains.json').unlink()
