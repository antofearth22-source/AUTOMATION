import pyotp
import time

class TotpManager:
    """
    Handles the generation and verification of Time-based One-Time Passwords (TOTP).
    """

    @staticmethod
    def get_totp_object(secret: str) -> pyotp.TOTP:
        """Creates a pyotp.TOTP object from a base32 secret key."""
        return pyotp.TOTP(secret)

    def verify_code(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verifies a TOTP code against a secret key.

        Args:
            secret: The base32 encoded secret key.
            code: The 6-digit TOTP code to verify.
            valid_window: The number of previous and future time intervals to check.
                          A window of 1 checks the current, previous, and next token.

        Returns:
            True if the code is valid, False otherwise.
        """
        if not secret or not code:
            return False

        totp = self.get_totp_object(secret)
        return totp.verify(code, valid_window=valid_window)

if __name__ == '__main__':
    # Test the TOTP verification process
    try:
        # Generate a new random secret for testing
        # In the real app, this will be loaded from the encrypted config
        test_secret = pyotp.random_base32()
        print(f"Using test secret: {test_secret}")

        totp_generator = TotpManager.get_totp_object(test_secret)

        # --- Test Case 1: Current code ---
        current_code = totp_generator.now()
        print(f"\nGenerated current code: {current_code}")
        is_valid = TotpManager().verify_code(test_secret, current_code)
        assert is_valid
        print(f"Verification with current code: {'PASSED' if is_valid else 'FAILED'}")

        # --- Test Case 2: Invalid code ---
        invalid_code = "000000"
        print(f"\nGenerated invalid code: {invalid_code}")
        is_valid = TotpManager().verify_code(test_secret, invalid_code)
        assert not is_valid
        print(f"Verification with invalid code: {'PASSED' if not is_valid else 'FAILED'}")

        # --- Test Case 3: Code from the past (within the valid window) ---
        print("\nWaiting for time window to shift to test past code...")
        time.sleep(30 - (time.time() % 30) + 1) # Wait for the next 30s interval

        new_code = totp_generator.now()
        print(f"Generated new code: {new_code}")
        print(f"Verifying with old code: {current_code}")
        is_valid_past = TotpManager().verify_code(test_secret, current_code, valid_window=1)
        assert is_valid_past
        print(f"Verification with past code (grace period): {'PASSED' if is_valid_past else 'FAILED'}")

        print("\nSUCCESS: All TOTP tests PASSED.")

    except Exception as e:
        print(f"\nERROR: TOTP tests FAILED: {e}")
