import configparser

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))

URL = config.get('SCHOOLLOOP', 'url')
USERNAME = config.get('SCHOOLLOOP', 'username')
PASSWORD = config.get('SCHOOLLOOP', 'password')