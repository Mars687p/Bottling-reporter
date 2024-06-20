from aiogram import types

from app.logs import logger
from app.services import users
from bot.services.auth import auth


@auth
@logger.catch
async def send_help(message: types.Message) -> types.Message:
    kb = [
        [types.KeyboardButton(text='Активные линии')],
        [types.KeyboardButton(text='Скорость линий')],
        [types.KeyboardButton(text='Режимы')]
        ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    if message.from_user is None:
        raise AttributeError
    text = (f'Здравствуйте, {users[message.from_user.id].name}\n'
            '/help - вызвать помощника \n'
            '<b>Активные линии</b> - получить информацию о обьеме и бутылках \n'
            '<b>Скорость линий</b> - получить среднюю скорость линий розлива \n'
            '<b>Режимы</b> - получить информацию о всех включенных режимах \n'
            )
    return await message.answer(text, reply_markup=keyboard)
