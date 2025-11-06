import os
import json
from dotenv import load_dotenv
from typing import Any, Dict
import sys

# This allows the script to be run directly for testing.
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.paths import resource_path

class ConfigManager:
    """
    Manages application configuration with a clear precedence:
    1. Environment variables
    2. .env file
    3. config.json file
    4. Default values
    """
    def __init__(self, data_dir_name: str = 'data'):
        self.base_path = resource_path()
        self.data_path = self.base_path / data_dir_name

        # Load .env file from the project root
        load_dotenv(dotenv_path=self.base_path / '.env')

        self.config_json_path = self.data_path / 'config.json'
        self.json_config = self._load_json_config()

        # Ensure data directory and default user files exist
        self._initialize_user_data_files()

    def _load_json_config(self) -> Dict[str, Any]:
        """Loads the base configuration from config.json."""
        if self.config_json_path.exists():
            with open(self.config_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value by key, following the precedence order.
        """
        # 1. Check Environment Variables (and .env file, handled by dotenv)
        value = os.getenv(key.upper())
        if value is not None:
            return value

        # 2. Check config.json
        value = self.json_config.get(key)
        if value is not None:
            return value

        # 3. Return default
        return default

    def _initialize_user_data_files(self):
        """Creates the data directory and default user data JSON files if missing."""
        self.data_path.mkdir(exist_ok=True)

        default_files = {
            'irctc_ids.json': {'accounts': []},
            'saved_tickets.json': {'tickets': []},
            'payment_options.json': {'upi': [], 'cards': []},
            'booking_history.json': {'history': []}
        }

        for filename, default_content in default_files.items():
            file_path = self.data_path / filename
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, indent=4)

    def load_user_data(self, filename: str) -> Dict[str, Any]:
        """Loads a specific user data JSON file (e.g., saved_tickets.json)."""
        file_path = self.data_path / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {} # Return empty dict if file doesn't exist

    def save_user_data(self, filename: str, data: Dict[str, Any]):
        """Saves data to a specific user data JSON file."""
        file_path = self.data_path / filename
        # Create a backup before writing
        if file_path.exists():
            file_path.rename(file_path.with_suffix('.json.bak'))

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        # Remove backup if save was successful
        backup_file = file_path.with_suffix('.json.bak')
        if backup_file.exists():
            backup_file.unlink()

if __name__ == '__main__':
    # This block allows for direct testing of the config manager.
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.utils.paths import resource_path

    # Test the new ConfigManager
    print("--- Testing ConfigManager ---")

    # Create a dummy .env file
    with open(resource_path('.env'), 'w') as f:
        f.write("PROVIDER=env_provider\n")
        f.write("LOG_LEVEL=DEBUG\n")

    # Create a dummy config.json
    dummy_config = {'PROVIDER': 'json_provider', 'MAX_RETRIES': 5}
    data_dir = resource_path('data')
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / 'config.json', 'w') as f:
        json.dump(dummy_config, f)

    config = ConfigManager()

    # Test precedence: env > json > default
    provider = config.get('PROVIDER', 'default_provider')
    log_level = config.get('LOG_LEVEL', 'INFO')
    max_retries = config.get('MAX_RETRIES', 3)
    default_val = config.get('MISSING_KEY', 'default_value')

    print(f"Provider: {provider} (Expected: env_provider)")
    print(f"Log Level: {log_level} (Expected: DEBUG)")
    print(f"Max Retries: {max_retries} (Expected: 5)")
    print(f"Missing Key: {default_val} (Expected: default_value)")

    assert provider == 'env_provider'
    assert log_level == 'DEBUG'
    assert max_retries == 5
    assert default_val == 'default_value'

    print("\nSUCCESS: ConfigManager tests passed.")

    # Cleanup dummy files
    (resource_path('.env')).unlink()
    (data_dir / 'config.json').unlink()
