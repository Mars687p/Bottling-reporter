import asyncio

from aiogram import F
from aiogram import types
from aiogram.filters.command import Command

from bot.services.config_bot import dp, bot

from bot.handlers.start import send_help
from bot.handlers.get_info_lines import get_info_working_lines, get_regime
from bot.handlers.speed_lines import get_speed_lines
from bot.handlers.set_volume_notify import set_value_to_stop, wait_number
from bot.keyboards.for_set_value import SetValueCallbackFactory
from bot.handlers.set_volume_notify import SetVolumeStates


async def register_handlers():
    dp.message.register(send_help, Command(commands=['start', 'help']))
    dp.message.register(get_info_working_lines, F.text == 'Активные линии')
    dp.message.register(get_speed_lines, F.text == 'Скорость линий')
    dp.message.register(get_regime, F.text == 'Режимы')
    
    dp.callback_query.register(wait_number, SetValueCallbackFactory.filter())
    dp.message.register(set_value_to_stop, SetVolumeStates.change_value)

async def register_commands():
    await bot.set_my_commands([types.BotCommand(command="help", description="Помощь")])