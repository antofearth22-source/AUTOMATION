import win32crypt
import base64

class CredentialManager:
    """
    Handles the encryption and decryption of sensitive data using the
    Windows Data Protection API (DPAPI).
    """

    @staticmethod
    def encrypt_data(plaintext: str) -> str:
        """
        Encrypts a string using DPAPI and returns a Base64-encoded string.

        Args:
            plaintext: The string to encrypt.

        Returns:
            A Base64-encoded string of the encrypted data.
        """
        if not isinstance(plaintext, str):
            raise TypeError("Input must be a string.")

        data_in = plaintext.encode('utf-8')
        data_out, _ = win32crypt.CryptProtectData(data_in, None, None, None, None, 0)
        return base64.b64encode(data_out).decode('utf-8')

    @staticmethod
    def decrypt_data(ciphertext: str) -> str:
        """
        Decrypts a Base64-encoded string that was encrypted with DPAPI.

        Args:
            ciphertext: The Base64-encoded encrypted string.

        Returns:
            The original decrypted string.
        """
        if not isinstance(ciphertext, str):
            raise TypeError("Input must be a string.")

        data_in = base64.b64decode(ciphertext.encode('utf-8'))
        data_out, _ = win32crypt.CryptUnprotectData(data_in, None, None, None, 0)
        return data_out.decode('utf-8')

if __name__ == '__main__':
    # Test the encryption and decryption process
    try:
        original_password = "MySuperSecretPassword123!"
        print(f"Original:    '{original_password}'")

        encrypted = CredentialManager.encrypt_data(original_password)
        print(f"Encrypted:   '{encrypted}'")

        decrypted = CredentialManager.decrypt_data(encrypted)
        print(f"Decrypted:   '{decrypted}'")

        assert original_password == decrypted
        print("\nSUCCESS: Encryption and decryption test PASSED.")
    except Exception as e:
        print(f"\nERROR: Encryption and decryption test FAILED: {e}")
        print("This module requires the 'pywin32' package and a Windows environment.")
