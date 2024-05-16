from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services import monitor_lines
from bot.keyboards.for_set_value import SetValueCallbackFactory
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.lines import Line

class SetVolumeStates(StatesGroup):
    change_value = State()

async def wait_number(callback: types.CallbackQuery, 
                            callback_data: SetValueCallbackFactory,
                            state: FSMContext):
    try:
        line = monitor_lines.tracking_lines[callback_data.value]
    except KeyError:
        return await callback.answer('Данная линия не активна')
    
    await callback.message.answer('Укажите число для остановки')
    await callback.answer()
    await state.set_data({'line': line})
    await state.set_state(SetVolumeStates.change_value)


async def set_value_to_stop(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
    except ValueError:
        return await message.answer('Введите число')
    line = await state.get_data()
    line: Line = line['line']

    line.volume_to_stop = value
    line.txtf_volume.value = value
    line.tg_notify[message.from_user.id]['is_on'] = 1
    line.tg_notify[message.from_user.id]['count'] = 0
    for switch in line.switch_tg_notify:
        if switch.data == message.from_user.id:
            switch.value = True
    
    await message.answer('Значение установлено!')
    await state.clear()

