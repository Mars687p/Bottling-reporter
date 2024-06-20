import asyncio
import json
from datetime import datetime
from typing import TYPE_CHECKING, Dict, TypedDict

from templates.sql_query import select_users_bot

if TYPE_CHECKING:
    from app.database import Database


class UserAccess(TypedDict):
    warning_bottling: int
    end_bottling: int
    night_warning: int
    value_warning: int
    set_volume_to_stop: int


class User:
    def __init__(self, tg_id: int,
                 name: str, family: str,
                 access: UserAccess) -> None:
        self.tg_id = tg_id
        self.name = name
        self.family = family
        self.access = access
        self.night_alerts_count: int = 0

    async def update_night_alerts(self, date_update: datetime) -> None:
        while True:
            if datetime.now().day == date_update.day:
                await asyncio.sleep(1800)
            else:
                self.access['night_warning'] = 1
                self.night_alerts_count = 0
                return


async def get_users(db_bot: 'Database') -> Dict[int, User]:
    response = await db_bot.select_sql(select_users_bot)
    if response is None:
        raise NotImplementedError
    return {int(user['tg_id']): User(user['tg_id'],
                                     user['first_name'],
                                     user['last_name'],
                                     UserAccess(json.loads(user['tg_access']))  # type: ignore
                                     )
            for user in response
            }
