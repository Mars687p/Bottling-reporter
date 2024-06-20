from typing import Callable, Literal

import asyncpg

from app.configuration import settings
from app.logs import logger


class Database:
    def __init__(self, user: str, type_db: Literal['bot', 'info']) -> None:
        self.user = user
        self.type_db = type_db
        self.config_database: dict = settings.get_conection_database(type_db)

    async def get_connection(self) -> bool:
        try:
            self.pool: asyncpg.Pool = await asyncpg.create_pool(
                                                host=self.config_database['host'],
                                                user=self.config_database['user'],
                                                password=self.config_database['password'],
                                                database=self.config_database['db_name'])
            return True
        except asyncpg.exceptions.ConnectionDoesNotExistError as _ex:
            logger.error(f'async - POSTGRES ERROR: Неверный пароль. {_ex}')
            return False

    async def select_sql(self, sql: str, *args: tuple) -> list[asyncpg.Record] | None:
        try:
            async with self.pool.acquire() as con:
                con: asyncpg.Connection  # type: ignore
                return await con.fetch(sql, *args)
        except asyncpg.exceptions.PostgresSyntaxError as _err:
            logger.error(f'async - POSTGRES_select_sql: {_err}')
            return None

    async def listen_db(self, listener: Callable) -> None:
        self.conn: asyncpg.Connection = await asyncpg.connect(
                                    host=self.config_database['host'],
                                    user=self.config_database['user'],
                                    password=self.config_database['password'],
                                    database=self.config_database['db_name'])
        # listen notify name
        await self.conn.add_listener('', listener)
        await self.conn.add_listener('', listener)
