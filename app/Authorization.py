import sys
from time import sleep
import requests
from ast import literal_eval
from app.Configuration import get_url_site, get_auth
from app.logs import logger


base_url = get_url_site()
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}


@logger.catch(onerror=lambda _: sys.exit(1))
def pass_authorization():
    login, password = get_auth()
    session = requests.Session()
    session.headers.update(HEADERS)
    login_url = base_url + 'login'
    while 'Authorization' not in HEADERS.keys():
        response = literal_eval(session.post(login_url, {
        'password': password,
        'username': login
        }).text)
        if 'token' in response.keys():
            HEADERS['Authorization'] = f'Bearer {response["token"]}'
            break
        logger.info('Авторизация не пройдена')
        sleep(5)
    HEADERS['Referer'] = base_url
    HEADERS['Accept'] = 'application/json'     
    session.headers.update(HEADERS)
    return session