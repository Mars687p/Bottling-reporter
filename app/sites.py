
import asyncio
import aiohttp

from typing import Optional, TYPE_CHECKING

from app.configuration import settings
from app.logs import logger

if TYPE_CHECKING:
    from app.gui import Gui_app


BASE_URL = settings.config.USER.URL_SITE

class SessionSite:
    def __init__(self) -> None:
        self.HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
        self.session: Optional[aiohttp.ClientSession] = None
        self.gui: Optional[Gui_app] = None

    async def execute_request(self, url):
        is_err = False  
        while True:
            try:
                async with self.session.get(url) as resp:

                    response = await resp.json()
                if is_err:
                    await self.gui.show_banner('Подключение восстановлено', 'info')
                return response
            except (TimeoutError, OSError, aiohttp.client_exceptions.ServerDisconnectedError,
                                                        asyncio.TimeoutError):
                if is_err == False: 
                    is_err = True 
                    self.gui.play_signal('Предупреждение')
                    await self.gui.show_banner('Нет связи с БАЗИС', 'err')
                await asyncio.sleep(5)
                
    @logger.catch
    async def pass_authorization(self) -> None:
        self.session = aiohttp.ClientSession(BASE_URL, headers=self.HEADERS)
        login = settings.config.USER.login
        password = settings.config.USER.password
        
        while 'Authorization' not in self.HEADERS.keys():
            async with self.session.post('/login', data={
                                                    'password': password,
                                                    'username': login
                                    }) as r:
                resp = await r.json()

            if 'token' in resp.keys():
                self.HEADERS['Authorization'] = f'Bearer {resp["token"]}'
                break
            logger.info('Авторизация не пройдена')
            await asyncio.sleep(5)

        self.HEADERS['Referer'] = BASE_URL + '/'
        self.HEADERS['Accept'] = 'application/json'  
        self.session.headers.update(self.HEADERS)  
    

    async def close_session(self) -> None:
        await self.session.close()


