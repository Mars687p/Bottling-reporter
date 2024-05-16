from aiogram import Bot, Dispatcher
from app.configuration import settings


bot = Bot(token=settings.config.BOT.TOKEN, parse_mode='HTML')
dp = Dispatcher()
