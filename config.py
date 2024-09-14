import configparser
import os


class CleanFileConfig:
    def __int__(self):
        self.age = 10
        self.base_path = ""
        self.config_path = ""


# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the properties file
CONFIG = CleanFileConfig()
script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG.config_path = f'{script_dir}/config.properties'
config.read(CONFIG.config_path)
CONFIG.age = int(config['settings']['age'])
CONFIG.base_path = config['settings']['clean_path']
