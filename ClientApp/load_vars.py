import configparser
import os


def get(section, key):
    _conf = configparser.ConfigParser()
    _conf.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return str(_conf[section][key])

def get_keys(section):
    _conf = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    #print(f"Reading config file at: {config_file_path}")  # Print path
    _conf.read(config_file_path)
    #print("Config sections:", _conf.sections())  # Print sections for debug
    return _conf.options(section)