from aiogram import types

from app.services import users
from app.logs import logger

def auth(func):
    async def wrapper(message: types.Message):
        if message.from_user.id not in users.keys():
            logger.warning(f'{message.from_user.username}: {message.from_user.id}.  Несанкционированная попытка входа в бота')
            return await message.answer('Несанкционированная попытка входа')
        return await func(message)
    return wrapper
