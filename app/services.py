import asyncio

from app.database import Database
from app.lines import MonitoringLines
from app.sites import SessionSite
from bot.services.users import get_users

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

db_bot = Database('bottling_reporter_bot', 'bot')
loop.run_until_complete(db_bot.get_connection())

users = loop.run_until_complete(get_users(db_bot))
site_worker = SessionSite()
monitor_lines = MonitoringLines(site_worker, users, db_bot)
