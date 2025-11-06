import win32crypt
import win32cred
import base64
import os
from src.utils.paths import resource_path

class CredentialManager:
    """
    Manages secure storage of credentials, prioritizing Windows Credential Manager
    with a fallback to DPAPI-encrypted local files.
    """
    SERVICE_NAME = "IRCTC_Pro"

    @staticmethod
    def _save_to_cred_manager(username: str, secret: str):
        """Saves a secret to the Windows Credential Manager."""
        win32cred.CredWrite({
            'TargetName': f"{CredentialManager.SERVICE_NAME}/{username}",
            'Type': win32cred.CRED_TYPE_GENERIC,
            'UserName': username,
            'CredentialBlob': secret.encode('utf-16le')
        }, 0)

    @staticmethod
    def _read_from_cred_manager(username: str) -> str | None:
        """Reads a secret from the Windows Credential Manager."""
        try:
            cred = win32cred.CredRead(f"{CredentialManager.SERVICE_NAME}/{username}", win32cred.CRED_TYPE_GENERIC)
            return cred['CredentialBlob'].decode('utf-16le')
        except Exception: # Catching a broad exception as the specific win32cred error is elusive
            return None

    @staticmethod
    def _save_to_dpapi_file(key: str, plaintext: str):
        """Encrypts data using DPAPI and saves it to a file."""
        data_dir = resource_path('data')
        data_dir.mkdir(exist_ok=True)
        filepath = data_dir / f"{key}.secure"

        data_in = plaintext.encode('utf-8')
        data_out, _ = win32crypt.CryptProtectData(data_in, None, None, None, None, 0)

        with open(filepath, 'wb') as f:
            f.write(base64.b64encode(data_out))

    @staticmethod
    def _read_from_dpapi_file(key: str) -> str | None:
        """Reads and decrypts data from a DPAPI-encrypted file."""
        filepath = resource_path('data', f"{key}.secure")
        if not filepath.exists():
            return None

        with open(filepath, 'rb') as f:
            ciphertext_b64 = f.read()

        data_in = base64.b64decode(ciphertext_b64)
        data_out, _ = win32crypt.CryptUnprotectData(data_in, None, None, None, 0)
        return data_out.decode('utf-8')

    @staticmethod
    def save_secret(key: str, secret: str):
        """Saves a secret, trying Credential Manager first, then DPAPI file."""
        try:
            CredentialManager._save_to_cred_manager(key, secret)
            print(f"Secret for '{key}' saved to Windows Credential Manager.")
        except Exception:
            print("Windows Credential Manager not available. Falling back to DPAPI file.")
            CredentialManager._save_to_dpapi_file(key, secret)
            print(f"Secret for '{key}' saved to local DPAPI-encrypted file.")

    @staticmethod
    def read_secret(key: str) -> str | None:
        """Reads a secret, trying Credential Manager first, then DPAPI file."""
        secret = CredentialManager._read_from_cred_manager(key)
        if secret is not None:
            return secret
        return CredentialManager._read_from_dpapi_file(key)


if __name__ == '__main__':
    # This test can only be run on a Windows machine.
    print("--- Testing CredentialManager on Windows ---")

    # Temporarily add project root to path for testing
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.utils.paths import resource_path

    try:
        test_key = "test_user_totp"
        original_secret = "MySuperSecretTOTPKey123!"

        print(f"Saving secret for key: '{test_key}'")
        CredentialManager.save_secret(test_key, original_secret)

        print(f"Reading secret for key: '{test_key}'")
        retrieved_secret = CredentialManager.read_secret(test_key)

        print(f"Original:  '{original_secret}'")
        print(f"Retrieved: '{retrieved_secret}'")

        assert original_secret == retrieved_secret
        print("\nSUCCESS: CredentialManager save/read test PASSED.")

    except Exception as e:
        print(f"\nERROR: Test failed. This module requires a Windows environment. Details: {e}")

    finally:
        # Clean up test file if it was created
        test_file = resource_path('data', f"{test_key}.secure")
        if test_file.exists():
            test_file.unlink()
            print(f"Cleaned up test file: {test_file}")
