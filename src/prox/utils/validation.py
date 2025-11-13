from datetime import date, timedelta

def is_journey_date_within_booking_window(
    journey_date: date,
    today: date,
    max_days: int = 120
) -> bool:
    """
    Validates if the journey date is within the allowed booking window.

    The window is from 'today' up to 'today + max_days'.

    Args:
        journey_date: The date of the journey to validate.
        today: The current date.
        max_days: The maximum number of days in advance for booking.

    Returns:
        True if the date is within the valid window, False otherwise.
    """
    if not isinstance(journey_date, date) or not isinstance(today, date):
        return False

    # The booking date must be on or after today
    if journey_date < today:
        return False

    # The booking date must be within the max_days limit
    booking_limit = today + timedelta(days=max_days)
    if journey_date > booking_limit:
        return False

    return True
