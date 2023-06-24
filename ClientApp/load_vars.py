import configparser
import os


def get(section, key):
    _conf = configparser.ConfigParser()
    _conf.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    return str(_conf[section][key])