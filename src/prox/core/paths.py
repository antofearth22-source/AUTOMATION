import os
from pathlib import Path

# This script is designed for Windows and relies on the APPDATA environment variable.
# A RuntimeError will be raised if it's not set.

appdata_path = os.getenv("APPDATA")
if not appdata_path:
    raise RuntimeError("APPDATA environment variable is not set. This application is designed for Windows.")

# Base application directory in Roaming AppData
APP_DIR = Path(appdata_path) / "Prox"

# Configuration directory
CONFIG_DIR = APP_DIR / "config"

# Data directory
DATA_DIR = APP_DIR / "data"

# Logs directory
LOGS_DIR = APP_DIR / "logs"

# Specific file paths
SETTINGS_FILE = CONFIG_DIR / "settings.json"
SECRETS_FILE = CONFIG_DIR / "secrets.json"
TICKET_TEMPLATES_FILE = DATA_DIR / "ticket_templates.json"

def ensure_app_dirs_exist():
    """
    Creates the necessary application directories if they do not already exist.
    This should be called once on application startup.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
