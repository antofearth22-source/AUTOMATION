from datetime import datetime
import pytz

class Clock:
    """
    A centralized, timezone-aware clock service for all time operations.
    This ensures all timestamps and calculations are consistent.
    """
    TIMEZONE = pytz.timezone('Asia/Kolkata')

    @staticmethod
    def now() -> datetime:
        """Returns the current time in the application's standard timezone."""
        return datetime.now(Clock.TIMEZONE)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Converts a timezone-aware datetime object to UTC."""
        return dt.astimezone(pytz.utc)

    @staticmethod
    def from_utc(dt: datetime) -> datetime:
        """Converts a UTC datetime object to the application's standard timezone."""
        return dt.astimezone(Clock.TIMEZONE)

    @staticmethod
    def is_tatkal_window(dt: datetime) -> bool:
        """
        Checks if the given datetime is within a Tatkal booking window.
        - AC Classes: 10:00 AM to 10:15 AM
        - Non-AC Classes: 11:00 AM to 11:15 AM
        """
        time_now = dt.time()

        # AC Tatkal Window
        if time_now >= datetime.strptime("10:00", "%H:%M").time() and \
           time_now <= datetime.strptime("10:15", "%H:%M").time():
            return True

        # Non-AC Tatkal Window
        if time_now >= datetime.strptime("11:00", "%H:%M").time() and \
           time_now <= datetime.strptime("11:15", "%H:%M").time():
            return True

        return False

if __name__ == '__main__':
    # Test the Clock service
    now_kolkata = Clock.now()
    print(f"Current Time (Asia/Kolkata): {now_kolkata.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

    now_utc = Clock.to_utc(now_kolkata)
    print(f"Current Time (UTC):          {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

    # Test Tatkal window logic
    test_time_ac = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 10, 5, 0))
    test_time_non_ac = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 11, 8, 0))
    test_time_outside = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 12, 0, 0))

    print(f"\nIs {test_time_ac.time()} in Tatkal window? {Clock.is_tatkal_window(test_time_ac)}")
    print(f"Is {test_time_non_ac.time()} in Tatkal window? {Clock.is_tatkal_window(test_time_non_ac)}")
    print(f"Is {test_time_outside.time()} in Tatkal window? {Clock.is_tatkal_window(test_time_outside)}")

    assert Clock.is_tatkal_window(test_time_ac)
    assert Clock.is_tatkal_window(test_time_non_ac)
    assert not Clock.is_tatkal_window(test_time_outside)

    print("\nSUCCESS: Clock service tests passed.")
