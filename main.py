import asyncio

import flet as ft

from app.bot import register_commands, register_handlers
from app.configuration import settings
from app.gui import Gui_app, new_process_report
from app.logs import logger
from app.services import db_bot, monitor_lines, site_worker, stop_event
from bot.services.config_bot import bot, dp


async def run_bot() -> None:
    await register_handlers()
    while True:
        try:
            await register_commands()
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except asyncio.CancelledError:
            break
        except Exception as e:
            if stop_event.is_set():
                return
            logger.error((
                f"Bot connection error: {e} \n"
                f"Retry reconnect via {settings.config.BASIC.retry_bot_timeout_sec} sec...")
            )
            await asyncio.sleep(settings.config.BASIC.retry_bot_timeout_sec)


async def start(page: ft.Page) -> None:
    gui = Gui_app(page, monitor_lines)
    page.add(gui)
    await gui.show_preload()
    site_worker.gui = gui

    await db_bot.get_connection()
    await site_worker.pass_authorization()
    await monitor_lines.get_working_lines()
    await gui.init_app()

    asyncio.create_task(monitor_lines.processing_new_data())
    if settings.config.BASIC.is_activate_bot:
        asyncio.create_task(run_bot())


if __name__ == '__main__':
    if settings.config.BASIC.only_reporter:
        new_process_report()
    else:
        ft.app(target=start)
