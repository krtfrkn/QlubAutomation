import json

class Configuration:
    
    def __init__(self):
        self.config_file_path = 'configuration.json'
        self.data = self._load_config()

    def _load_config(self):
        with open(self.config_file_path, "r") as config_file:
            return json.load(config_file)

    def get(self, key):
        return self.data.get(key)