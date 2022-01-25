import sys   
import configparser
from app.logs import logger


try:
    config = configparser.ConfigParser()
    config.read('config.ini')
except Exception as e:
    logger.exception(e)
    sys.exit()

def get_url_site():
    return config.get('User', 'url_site')
    
def get_auth():
    login = config.get('User', 'login')
    password = config.get('User', 'password')
    return login, password

def get_name_signal(name_line):
    name_signal ={'Линия розлива №1':'line1', 'Линия розлива №2':'line2', 'Спиртоприемное отделение': 'spirt',
                  'Линия розлива №3': 'line3', 'Производство дистиллятов': 'distillate'}
    return config.get('Audio', name_signal[name_line])

def get_bot_token():
    return config.get('Bot', 'token')

def get_user_id():
    return [int(i) for i in config.get('Bot', 'userID').split(', ')]