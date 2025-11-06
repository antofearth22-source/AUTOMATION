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
    4. Default values from the class
    """
    def __init__(self, data_dir_name: str = 'data'):
        self.base_path = resource_path()
        self.data_path = self.base_path / data_dir_name

        # Load .env file from the project root
        load_dotenv(dotenv_path=self.base_path / '.env')

        self.config_json_path = self.data_path / 'config.json'
        self.json_config = self._load_or_create_json_config()

        # Ensure data directory and default user files exist
        self._initialize_user_data_files()

    def _load_or_create_json_config(self) -> Dict[str, Any]:
        """Loads config.json or creates it with defaults if it doesn't exist."""
        if self.config_json_path.exists():
            with open(self.config_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Define the default configuration structure
            default_config = {
                "CAPTCHA_SOLVER_PATH": "path/to/your/captcha_solver.exe",
                "LOG_LEVEL": "INFO",
                "MAX_RETRIES": 3
            }
            # Ensure the data directory exists before writing
            self.data_path.mkdir(exist_ok=True)
            with open(self.config_json_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
            return default_config

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
        return {}

    def save_user_data(self, filename: str, data: Dict[str, Any]):
        """Saves data to a specific user data JSON file."""
        file_path = self.data_path / filename
        if file_path.exists():
            file_path.rename(file_path.with_suffix('.json.bak'))

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        backup_file = file_path.with_suffix('.json.bak')
        if backup_file.exists():
            backup_file.unlink()

# ... (rest of the file is unchanged)
