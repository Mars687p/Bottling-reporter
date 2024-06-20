from aiogram import types

from app.logs import logger
from app.services import monitor_lines
from bot.services.auth import auth


@auth
@logger.catch
async def get_speed_lines(message: types.Message) -> types.Message:
    if message.from_user is None:
        raise AttributeError
    logger.info(f'{message.from_user.username}: {message.from_user.id}. Запрос скорости линий')

    lines = monitor_lines.tracking_lines
    if len(lines) == 0:
        return await message.answer('Нет активных линий')
    txt = ''
    for line in lines.values():
        total_speed = await line.get_speed_line_total_now()
        txt += (f'<b>{line.name_line}</b>\n'
                f'<b>Скорость:</b> \n'
                f'<b>За последние 10 мин. -</b> {line.average_speed_10m} в час.\n'
                f'<b>За последний час -</b> {line.average_speed_h} в час.\n'
                f'<b>Ср. скорость за розлив -</b> {total_speed} в час.\n')

        txt += '\n\n'

    return await message.answer(txt)
