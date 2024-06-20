import asyncio

import flet as ft

from app.bot import bot, dp, register_commands, register_handlers
from app.configuration import settings
from app.gui import Gui_app, new_process_report
from app.services import db_bot, monitor_lines, site_worker


async def start(page: ft.Page) -> None:
    try:
        gui = Gui_app(page, monitor_lines)
        page.add(gui)
        await gui.show_preload()
        site_worker.gui = gui

        await db_bot.get_connection()
        await site_worker.pass_authorization()
        await monitor_lines.get_working_lines()
        await gui.init_app()
        asyncio.create_task(monitor_lines.processing_new_data())

        await register_handlers()
        await register_commands()
        await dp.start_polling(bot)
    finally:
        await site_worker.close_session()
        await db_bot.pool.close()

if __name__ == '__main__':
    if settings.config.BASIC.only_reporter:
        new_process_report()
    else:
        ft.app(target=start)
