from aiogram import types

from app.logs import logger
from app.services import monitor_lines, users

from bot.services.auth import auth
from bot.keyboards.for_set_value import kb_pick_line


@auth
@logger.catch
async def get_info_working_lines(message: types.Message):
    logger.info(f'{message.from_user.username}: {message.from_user.id}. Запрос информации')
    lines = monitor_lines.tracking_lines
    if len(lines) == 0: return await message.answer('Нет активных линий')

    txt: str = ''
    kb = None

    for line in lines.values():
        txt += (f'<b>{line.name_line}</b>\n'
                 f'{line.name_product}.\n'
                 f'<b>Обьем:</b> {line.alcovolume} дал.\n'
                 f'<b>Бутылки:</b> {line.bottle_count} шт.\n')
        
        if users[message.from_user.id].access['value_warning']:
            if line.volume_to_stop == '':
                volume_to_stop = '<b>НЕТ</b>'
            else:
                volume_to_stop = f'<b>{line.volume_to_stop}</b> дал'
            txt += f'Значения оповещения: {volume_to_stop}.'

        txt += '\n\n'
    if users[message.from_user.id].access['set_volume_to_stop']:
        kb = await kb_pick_line(lines)
    await message.answer(txt, reply_markup=kb)


@auth
@logger.catch
async def get_regime(message: types.Message, users=None):
    logger.info(f'{message.from_user.username}: {message.from_user.id}. Запрос режимов')
    text = await monitor_lines.get_regime_lines()
    await message.answer(text)