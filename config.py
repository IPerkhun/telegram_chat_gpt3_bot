import os
from configparser import ConfigParser

class ConfigManager:
    def __init__(self, config_file_path='config-dev.ini'):
        self.config_file_path = config_file_path
        self.config = ConfigParser()
        self.config.read(self.config_file_path)

    def get(self, section='default', key=None):
        if key is None:
            return self.config.items(section)
        else:
            return self.config.get(section, key)
        
    def get_tg_bot_token(self):
        return self.get('default', 'TELEGRAM_BOT_TOKEN')
    
    def get_openai_api_key(self):
        return self.get('default', 'OPEN_AI_API_KEY')
    
