from bot.services.config_bot import bot


async def close_bot_connection() -> None:
    await bot.session.close()
