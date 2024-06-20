from typing import TYPE_CHECKING

from bot.services.config_bot import bot

if TYPE_CHECKING:
    from app.lines import Line


async def send_warning(line: 'Line', tg_id: int) -> None:
    await bot.send_message(tg_id, f'{line.name_line} готова к остановке.')


async def send_completed_bottling(line: 'Line',
                                  speed_in_h: int,
                                  tg_id: int) -> None:
    text = f'<b>Розлив закрыт.</b> {line.name_line}: {line.bottle_count} шт.\n'
    if speed_in_h != 0:
        text += f'<b>Средняя скорость: </b> {speed_in_h} в час.'
    await bot.send_message(tg_id, text)


async def send_night_warning(item: dict, tg_id: int) -> None:
    text = f"{item['lineName']}. <b>Открыт режим в ночное время</b>"
    await bot.send_message(tg_id, text)


async def send_calling_supervisor(fio: str, tg_id:  int) -> None:
    text = (f"Уважаемая {fio}!\n",
            "Придите к нам пожалуйста, когда у вас будет свободная минутка&#128522;")
    await bot.send_message(tg_id, text)
