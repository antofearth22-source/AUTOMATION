import unittest
import os
import sys
from datetime import datetime
import pytz

# Add the project root to the path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.clock import Clock

class TestClock(unittest.TestCase):

    def test_now_is_timezone_aware(self):
        """Tests that Clock.now() returns a timezone-aware datetime object."""
        now_time = Clock.now()
        self.assertIsNotNone(now_time.tzinfo)
        self.assertEqual(now_time.tzinfo.zone, 'Asia/Kolkata')

    def test_utc_conversion(self):
        """Tests the conversion to and from UTC."""
        now_kolkata = Clock.now()
        now_utc = Clock.to_utc(now_kolkata)
        self.assertEqual(now_utc.tzinfo.zone, 'UTC')

        converted_back = Clock.from_utc(now_utc)
        self.assertEqual(converted_back, now_kolkata)

    def test_tatkal_window_logic(self):
        """Tests the is_tatkal_window method with various times."""
        # AC Tatkal Window (10:00 - 10:15)
        ac_start = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 10, 0, 0))
        ac_middle = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 10, 8, 30))
        ac_end = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 10, 15, 0))

        # Non-AC Tatkal Window (11:00 - 11:15)
        non_ac_start = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 11, 0, 0))
        non_ac_middle = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 11, 8, 30))
        non_ac_end = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 11, 15, 0))

        # Outside windows
        before_ac = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 9, 59, 59))
        between = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 10, 30, 0))
        after_non_ac = Clock.TIMEZONE.localize(datetime(2025, 1, 1, 11, 15, 1))

        self.assertTrue(Clock.is_tatkal_window(ac_start))
        self.assertTrue(Clock.is_tatkal_window(ac_middle))
        self.assertTrue(Clock.is_tatkal_window(ac_end))

        self.assertTrue(Clock.is_tatkal_window(non_ac_start))
        self.assertTrue(Clock.is_tatkal_window(non_ac_middle))
        self.assertTrue(Clock.is_tatkal_window(non_ac_end))

        self.assertFalse(Clock.is_tatkal_window(before_ac))
        self.assertFalse(Clock.is_tatkal_window(between))
        self.assertFalse(Clock.is_tatkal_window(after_non_ac))

if __name__ == '__main__':
    unittest.main()
