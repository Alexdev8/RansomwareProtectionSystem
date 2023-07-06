import configparser
import os

# os.path.join(os.path.dirname(__file__),
def get(section, key):
    _conf = configparser.ConfigParser()
    _conf.read('config.ini')
    return str(_conf[section][key])

def get_keys(section):
    _conf = configparser.ConfigParser()
    config_file_path = 'config.ini'
    #print(f"Reading config file at: {config_file_path}")  # Print path
    _conf.read(config_file_path)
    #print("Config sections:", _conf.sections())  # Print sections for debug
    return _conf.options(section)

def get_values(section):
    _conf = configparser.ConfigParser()
    config_file_path = 'config.ini'
    _conf.read(config_file_path)
    return [value for key, value in _conf.items(section)]
