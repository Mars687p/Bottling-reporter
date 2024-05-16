import json, asyncio
from datetime import datetime
from templates.sql_query import  select_users_bot

class User:
    def __init__(self, tg_id, name, family, access) -> None:
        self.tg_id = tg_id
        self.name: str = name
        self.family: str = family
        self.access: dict = access
        self.night_alerts_count: int = 0

    async def update_night_alerts(self, date_update: datetime):
        while True:
            if datetime.now().day == date_update.day:
                await asyncio.sleep(1800)
            else:    
                self.access['night_warning'] = 1
                self.night_alerts_count = 0
                return

async def get_users(db_bot) -> dict:
    return {int(user['tg_id']): User(user['tg_id'], 
                                     user['first_name'], 
                                     user['last_name'],
                                     json.loads(user['tg_access']))
                                for user in  await db_bot.select_sql(select_users_bot)
    }
