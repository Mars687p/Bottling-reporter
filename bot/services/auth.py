from typing import Any, Callable

from aiogram import types

from app.logs import logger
from app.services import users


def auth(func: Callable) -> Callable:
    async def wrapper(message: types.Message) -> Any:
        if message.from_user is not None:
            if message.from_user.id not in users.keys():
                logger.warning(
                        (f'{message.from_user.username}: {message.from_user.id}. ',
                         'Несанкционированная попытка входа в бота')
                              )
                return await message.answer('Несанкционированная попытка входа')
        return await func(message)
    return wrapper
