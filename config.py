import configparser
import os


class CleanFileConfig:
    def __int__(self):
        self.age = 10
        self.base_path = ""
        self.config_path = ""
        self.telegram_token = ""
        self.telegram_conversation_id = -1
        self.cpu_threshold = 50.0
        self.memory_threshold = 50.0
        self.disk_threshold = 50.0
        self.db_master = ""
        self.db_master_db = ""
        self.db_master_port = 5432
        self.db_master_user = ""
        self.db_master_password = ""
        self.db_slaves = ""
        self.elastic_search = ""
        self.elastic_api_key = ""
        self.elastic_enable = True
        self.elastic_index = ""
        self.index_replica = ""
        self.index_login = ""
        self.slow_query_duration = 1000
        self.slow_query_rows = 10000
        self.white_list_ip = []
        self.connection_log_path= ""
        self.refresh_mv_path = ""
        self.push_api_enable=False
        self.push_api_host = ""
        self.push_api_key = ""
        self.mode = ""
        self.isDev = False
        self.server_name = ''
        self.server_ip = ''

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the properties file
CONFIG = CleanFileConfig()
script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG.config_path = f'{script_dir}/config.properties'
config.read(CONFIG.config_path)
CONFIG.age = int(config['settings']['age'])
CONFIG.base_path = config['settings']['clean_path']
CONFIG.mode = config['settings']['mode']
CONFIG.isDev = CONFIG.mode == 'development' 
CONFIG.telegram_token = config["telegram"]["token"]
CONFIG.telegram_conversation_id = config["telegram"]["conversation_id"]
CONFIG.cpu_threshold = float(config["monitor"]["cpu_threshold"])
CONFIG.memory_threshold = float(config["monitor"]["memory_threshold"])
CONFIG.disk_threshold = float(config["monitor"]["disk_threshold"])
CONFIG.db_master = config["postgres"]["db_master"]
CONFIG.db_master_user = config["postgres"]["db_master_user"]
CONFIG.db_master_password = config["postgres"]["db_master_password"]
CONFIG.db_master_port = int(config["postgres"]["db_master_port"])
CONFIG.db_master_db = config["postgres"]["db_master_db"]
CONFIG.db_slaves = config["postgres"]["db_slaves"]
CONFIG.slow_query_duration = int(config["postgres"]["slow_query_duration"])
CONFIG.slow_query_rows = int(config['postgres']['slow_query_rows'])
CONFIG.elastic_enable = False if config["elastic"]["enable"] == 'false' else True
CONFIG.elastic_search = config["elastic"]["host"]
CONFIG.elastic_api_key = config["elastic"]["api_key"]
CONFIG.elastic_index = config["elastic"]["index"]
CONFIG.index_replica = config["elastic"]["index_replica"]
CONFIG.index_login = config["elastic"]["index_login"]
CONFIG.white_list_ip = config["connection"]["white_list"].split(",")
CONFIG.connection_log_path =  config["connection"]["log_path"]
CONFIG.refresh_mv_path = config["refresh_mv"]["path"]
CONFIG.push_api_enable = False if config["push_log"]["api_enable"] == 'false'  else True
CONFIG.push_api_host = config["push_log"]["api_host"]
CONFIG.push_api_key = config["push_log"]["api_key"]
CONFIG.server_name = config['server']['server_name']
CONFIG.server_ip = config['server']['server_ip']