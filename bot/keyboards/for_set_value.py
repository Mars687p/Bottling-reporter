from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


from typing import TYPE_CHECKING, Dict, Optional
if TYPE_CHECKING:
    from app.lines import Line


class SetValueCallbackFactory(CallbackData, prefix="volume"):
    action: str
    value: Optional[str] = None


async def kb_pick_line(lines: Dict[str, 'Line']) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for line in lines.values():
        builder.button(
            text=line.name_line, callback_data=SetValueCallbackFactory(action="set", value=line.name_line)
        )
    builder.adjust(1)
    return builder.as_markup()
     