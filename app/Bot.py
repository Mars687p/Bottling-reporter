from aiogram import F, types
from aiogram.filters.command import Command

from bot.handlers.get_info_lines import get_info_working_lines, get_regime
from bot.handlers.set_volume_notify import (SetVolumeStates, set_value_to_stop,
                                            wait_number)
from bot.handlers.speed_lines import get_speed_lines
from bot.handlers.start import send_help
from bot.keyboards.for_set_value import SetValueCallbackFactory
from bot.services.config_bot import bot, dp


async def register_handlers() -> None:
    dp.message.register(send_help, Command(commands=['start', 'help']))
    dp.message.register(get_info_working_lines, F.text == 'Активные линии')
    dp.message.register(get_speed_lines, F.text == 'Скорость линий')
    dp.message.register(get_regime, F.text == 'Режимы')

    dp.callback_query.register(wait_number, SetValueCallbackFactory.filter())
    dp.message.register(set_value_to_stop, SetVolumeStates.change_value)


async def register_commands() -> None:
    await bot.set_my_commands([
                                types.BotCommand(command="help",
                                                 description="Помощь")
                              ]
                              )
