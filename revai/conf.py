import configparser
from Crypto.Random import get_random_bytes
config = configparser.ConfigParser()
config.read('revai/db.ini')

DB_PWD = config['Database']['DB_PWD']
with open('revai/key.bin', 'rb') as f:
    key = f.read()