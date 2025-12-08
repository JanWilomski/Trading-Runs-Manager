import json
import os

class SettingsManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        if not os.path.exists(settings_path):
            self.create_default_settings()
        self.settings = self.load_settings()

    def load_settings(self):
        with open(self.settings_path, 'r') as f:
            return json.load(f)


    def save_settings(self, settings):
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_setting(self, key):
        return self.settings.get(key)
    def set_setting(self, key, value):
        settings = self.settings
        settings[key] = value
        self.save_settings(settings)

    def create_default_settings(self):
        self.save_settings({
          "master_password_hash": "",
          "default_max_loss_percentage": 50,
          "default_max_daily_loss_percentage": 25,
          "theme": "dark",
          "last_used_account_id": None
        })

    def settings_exist(self):
        return os.path.exists(self.settings_path)