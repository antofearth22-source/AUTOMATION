import os
import json

class ConfigManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.config_files = {
            'app_config': os.path.join(self.data_dir, 'app_config.json'),
            'irctc_ids': os.path.join(self.data_dir, 'irctc_ids.json'),
            'saved_tickets': os.path.join(self.data_dir, 'saved_tickets.json'),
            'payment_options': os.path.join(self.data_dir, 'payment_options.json'),
            'station_list': os.path.join(self.data_dir, 'stationlist.json'),
            'booking_history': os.path.join(self.data_dir, 'booking_history.json')
        }
        self.ensure_data_dir_exists()
        self.create_default_configs()

    def ensure_data_dir_exists(self):
        """Creates the data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def create_default_configs(self):
        """Creates default configuration files if they are missing."""
        default_structures = {
            'app_config': {},
            'irctc_ids': {'accounts': []},
            'saved_tickets': {'tickets': []},
            'payment_options': {'upi': [], 'cards': []},
            'station_list': {'stations': []},
            'booking_history': {'history': []}
        }

        for name, path in self.config_files.items():
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(default_structures[name], f, indent=4)

    def load_config(self, name):
        """Loads a specific JSON configuration file."""
        path = self.config_files.get(name)
        if path and os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def save_config(self, name, data):
        """Saves data to a specific JSON configuration file."""
        path = self.config_files.get(name)
        if path:
            # Create a backup before writing
            if os.path.exists(path):
                os.rename(path, path + '.bak')

            with open(path, 'w') as f:
                json.dump(data, f, indent=4)

            # Remove backup if save was successful
            if os.path.exists(path + '.bak'):
                os.remove(path + '.bak')

if __name__ == '__main__':
    # This allows for testing the config manager independently
    config_manager = ConfigManager()
    print(f"Data directory '{config_manager.data_dir}' is ready.")
    for name, path in config_manager.config_files.items():
        print(f"Config file '{path}' is {'present' if os.path.exists(path) else 'missing'}.")
