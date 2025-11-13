import json
from typing import List, Optional
from src.prox.core import paths
from src.prox.models.base_models import IRCTCAccount

class SecretsManager:
    """
    Manages loading and saving IRCTC account credentials from secrets.json.

    NOTE: In this version, secrets are stored in plain text. Future versions
    will use Windows DPAPI for encryption via the placeholder methods.
    """
    def __init__(self):
        # Ensure the directories exist before any file operations
        paths.ensure_app_dirs_exist()

    def _encrypt(self, plaintext: str) -> str:
        """Placeholder for future encryption logic (e.g., using win32crypt)."""
        return plaintext

    def _decrypt(self, ciphertext: str) -> str:
        """Placeholder for future decryption logic (e.g., using win32crypt)."""
        return ciphertext

    def load_accounts(self) -> List[IRCTCAccount]:
        """
        Loads all IRCTC accounts from secrets.json.
        If the file doesn't exist, it returns an empty list.
        """
        if not paths.SECRETS_FILE.exists():
            return []

        try:
            with open(paths.SECRETS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            accounts = []
            for item in data:
                # "Decrypt" the password before validating the model
                item['password'] = self._decrypt(item.get('password', ''))
                accounts.append(IRCTCAccount.model_validate(item))
            return accounts
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_accounts(self, accounts: List[IRCTCAccount]):
        """
        Saves a list of IRCTC accounts to secrets.json.
        Passwords are "encrypted" before saving.
        """
        account_data = []
        for acc in accounts:
            data = acc.model_dump()
            # "Encrypt" the password before writing to disk
            data['password'] = self._encrypt(data.get('password', ''))
            account_data.append(data)

        with open(paths.SECRETS_FILE, "w", encoding="utf-8") as f:
            json.dump(account_data, f, indent=4)

    def get_account_by_username(self, username: str) -> Optional[IRCTCAccount]:
        """Retrieves a single account by its username."""
        accounts = self.load_accounts()
        for acc in accounts:
            if acc.username == username:
                return acc
        return None
