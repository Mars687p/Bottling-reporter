from aiogram import types

from app.logs import logger
from bot.services.auth import auth
from app.services import users

@auth
@logger.catch
async def send_help(message: types.Message):
    kb = [
        [types.KeyboardButton(text= 'Активные линии')],
        [types.KeyboardButton(text='Скорость линий')],
        [types.KeyboardButton(text='Режимы')]
        ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    text = (f'Здравствуйте, {users[message.from_user.id].name}\n'
            '/help - вызвать помощника \n'
            '<b>Активные линии</b> - получить информацию о обьеме и бутылках \n'
            '<b>Скорость линий</b> - получить среднюю скорость линий розлива \n'
            '<b>Режимы</b> - получить информацию о всех включенных режимах \n'
            )
    await message.answer(text, reply_markup=keyboard)