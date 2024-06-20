import asyncio
from datetime import datetime
from typing import (TYPE_CHECKING, Dict, Literal, Never, Optional, TypedDict,
                    Union)

import flet as ft

from app.configuration import settings
from app.logs import logger
from app.sites import SessionSite
from bot.handlers.send_msg import (send_completed_bottling, send_night_warning,
                                   send_warning)
from templates import sql_query

if TYPE_CHECKING:
    import asyncpg

    from app.database import Database
    from app.gui import Gui_app
    from bot.services.users import User


class IntervData(TypedDict):
    bottle_count: int
    create_time: datetime


class TgNotify(TypedDict):
    is_on: bool
    count: int


class Line:
    def __init__(self, gui: 'Gui_app',
                 url: str,
                 point_control: int,
                 name: str,
                 product: str,
                 regime: int,
                 beg_time: str,
                 users: Dict[int, 'User'],
                 volume_to_stop: Union[Literal[''], float] = '',
                 signal: bool = True):
        self.gui = gui
        self.url_line = url
        self.point_control = point_control
        self.name_line = name
        self.name_product = product
        self.regime = regime
        self.beg_time = datetime.strptime(beg_time, '%Y-%m-%dT%H:%M:%SZ')
        self.users = users

        self.over_alko_volume = 0.0
        self.alcovolume = 0.0
        self.over_bottles_count = 0
        self.bottle_count = 0

        # interv time
        self.interv_data: list[IntervData] = []
        # speed in the last 10 minutes. per_hour
        self.average_speed_10m: int = 0
        self.average_speed_h: int = 0

        self.volume_to_stop = volume_to_stop
        self.signal_active = signal

        self.tg_notify: Dict[int, TgNotify] = {}

        self.is_work = True

    async def _change_tg_notify(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            self.tg_notify[e.control.data]['is_on'] = True
            self.tg_notify[e.control.data]['count'] = 0
        else:
            self.tg_notify[e.control.data]['is_on'] = False

    async def create_cl_line(self) -> None:
        self.switch_tg_notify = []
        for tg_id, user in self.users.items():
            if user.access['warning_bottling']:
                self.tg_notify[tg_id] = TgNotify(is_on=False,
                                                 count=0)
                chck = ft.Switch(
                                label=f"Оповестить в ТГ: {user.name}",
                                expand_loose=True,
                                height=30,
                                data=tg_id,
                                on_change=self._change_tg_notify
                                )
                self.switch_tg_notify.append(chck)

        self.txt_name_line = ft.Text(self.name_line,
                                     text_align=ft.TextAlign.CENTER,
                                     size=20,
                                     weight=ft.FontWeight.BOLD,
                                     max_lines=2,
                                     expand=True)

        self.txt_name_product = ft.Text(self.name_product,
                                        text_align=ft.TextAlign.CENTER,
                                        size=12,
                                        max_lines=2,
                                        selectable=True)

        self.txt_volume = ft.Text(str(self.alcovolume),
                                  text_align=ft.TextAlign.CENTER,
                                  size=28,
                                  weight=ft.FontWeight.BOLD,
                                  expand=True,
                                  selectable=True)

        self.txtf_volume = ft.TextField(label='Оповестить при, дал',
                                        text_align=ft.TextAlign.CENTER,
                                        border_width=2,
                                        border_color=ft.colors.BLACK,
                                        bgcolor=ft.colors.WHITE,
                                        dense=True,
                                        text_style=ft.TextStyle(
                                                    weight=ft.FontWeight.BOLD,
                                                    size=24)
                                        )

        self.txt_bottles = ft.Text(str(self.bottle_count),
                                   text_align=ft.TextAlign.CENTER,
                                   size=14,
                                   weight=ft.FontWeight.BOLD,
                                   selectable=True,
                                   expand=True)

        self.txt_speed_line = ft.Text(
                                    f'{self.average_speed_10m} в час.',
                                    text_align=ft.TextAlign.CENTER,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    selectable=True,
                                    expand=True)

        self.cont_txt_bottles = ft.Container(
                                    self.txt_bottles,
                                    border=ft.border.all(1, ft.colors.BLACK),
                                    border_radius=ft.border_radius.all(10),
                                    padding=ft.padding.symmetric(horizontal=10),
                                    )

        self.cont_txt_speed_line = ft.Container(
                                        self.txt_speed_line,
                                        border=ft.border.all(1, ft.colors.BLACK),
                                        border_radius=ft.border_radius.all(10),
                                        padding=ft.padding.symmetric(horizontal=10),
                                        )
        row_bottle_info = ft.Row(
                                [
                                    self.cont_txt_bottles,
                                    self.cont_txt_speed_line
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                                )

        # if date = true, then alerts are on
        self.but_notify_on_off = ft.ElevatedButton(
                                    content=ft.Text('Отключить оповещения',
                                                    color=ft.colors.BLACK,
                                                    expand=True),
                                    bgcolor='#90EE90', height=50, data=True,
                                    on_click=self.get_signal_active)

        self.cont_txt_volume = ft.Container(
                                        self.txt_volume,
                                        border=ft.border.all(2, ft.colors.BLACK),
                                        border_radius=ft.border_radius.all(10),
                                        padding=ft.padding.symmetric(horizontal=10),
                                        bgcolor=ft.colors.WHITE
                                        )

        cl_lines = ft.Column(
                        controls=[
                            ft.Container(
                                self.txt_name_line,
                                border=ft.border.only(
                                            bottom=ft.BorderSide(
                                                        2,
                                                        ft.colors.BLACK)),
                                bgcolor='#00FF00',
                                border_radius=ft.border_radius.vertical(top=10),
                                alignment=ft.alignment.center
                                ),
                            ft.Container(
                                self.txt_name_product,
                                padding=ft.padding.symmetric(horizontal=5)
                                ),
                            ft.Container(
                                row_bottle_info,
                                padding=ft.padding.symmetric(horizontal=5)
                                ),
                            ft.Container(
                                self.cont_txt_volume,
                                padding=ft.padding.symmetric(horizontal=5)
                                ),
                            ft.Container(
                                self.txtf_volume,
                                padding=ft.padding.symmetric(horizontal=5)
                                ),
                            ft.Container(
                                self.but_notify_on_off,
                                padding=ft.padding.symmetric(horizontal=5)
                                ),
                            *self.switch_tg_notify
                            ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.START,
                        )
        content = ft.Container(
                                cl_lines,
                                bgcolor='#F0FFF0',
                                border=ft.border.all(2, ft.colors.BLACK),
                                border_radius=ft.border_radius.all(10),
                                padding=0,
                                width=300,
                                height=410,
                                data=self.name_line
                            )
        self.gui_elements = content

    async def get_signal_active(self, e=None) -> None:
        self.signal_active *= -1
        if self.signal_active == 1:
            if self.but_notify_on_off.content is not None:

                self.but_notify_on_off.content.value = 'Отключить оповещение'
            self.but_notify_on_off.bgcolor = '#90EE90'
            self.but_notify_on_off.data = True
        else:
            self.but_notify_on_off.content.value = 'Включить оповещение'
            self.but_notify_on_off.bgcolor = ft.colors.RED
            self.but_notify_on_off.data = False
            self.gui.stop_signal()
        self.gui.page.update()

    @logger.catch
    async def write_history_regime(self, db_bot: 'Database') -> None:
        async with db_bot.pool.acquire() as con:
            con: asyncpg.Connection
            row = await con.fetchrow(sql_query.select_entry, self.point_control, self.beg_time)
            if row is None:
                await con.execute(
                                sql_query.insert_history_regime,
                                self.point_control, self.name_product, self.regime,
                                self.over_alko_volume, self.over_bottles_count,
                                self.beg_time
                                )

    @logger.catch
    async def update_history_regime(self, db_bot: 'Database', end_time) -> None:
        async with db_bot.pool.acquire() as con:
            con: asyncpg.Connection
            await con.execute(
                            sql_query.add_end_time_regime,
                            self.bottle_count, self.alcovolume,
                            datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ'),
                            self.point_control, self.beg_time
                            )

    @logger.catch
    async def get_speed_line_total_db(self, db_bot) -> int:
        async with db_bot.pool.acquire() as con:
            regime = await con.fetch(sql_query.select_regime_line,
                                     self.beg_time,
                                     self.point_control)
        if len(regime) > 0:
            regime = regime[0]
            delta_time = (regime['end_time'] - regime['beg_time']).seconds
            # Вычитаем обед
            if regime['beg_time'].hour < 12 and regime['end_time'].hour >= 13:
                delta_time -= 3600
            try:
                return int(self.bottle_count/(delta_time/3600))
            except ZeroDivisionError:
                pass
        return 0

    @logger.catch
    async def get_speed_line_total_now(self) -> int:
        now = datetime.now()
        delta_time = (now - self.beg_time).seconds
        # Вычитаем обед
        if self.beg_time.hour < 12 and now.hour >= 13:
            delta_time -= 3600
        try:
            return int(self.bottle_count/(delta_time/3600))
        except ZeroDivisionError:
            return 0

    @logger.catch
    async def get_speed_line_per_h(self) -> None:
        if len(self.interv_data) < 2:
            return

        current_data = self.interv_data[-1]
        time_sec = (current_data['create_time'] - self.interv_data[0]['create_time']).seconds + 1
        if time_sec < 3600:
            bottles = current_data['bottle_count'] - self.interv_data[0]['bottle_count']
            self.average_speed_h = int(bottles/time_sec*3600)
            return

        for time_interval in self.interv_data[::-1]:
            time_sec = (current_data['create_time'] - time_interval['create_time']).seconds + 1
            if time_sec >= 3600:
                bottles = current_data['bottle_count'] - time_interval['bottle_count']
                self.average_speed_h = int(bottles/time_sec*3600)
                break

    @logger.catch
    async def get_speed_line_per_10m(self, period) -> None:
        if len(self.interv_data) < 2:
            return
        current_data = self.interv_data[-1]

        for time_interval in self.interv_data[::-1]:
            time_sec = (current_data['create_time'] - time_interval['create_time']).seconds + 1
            if time_sec >= period:
                bottles = current_data['bottle_count'] - time_interval['bottle_count']
                self.average_speed_10m = int(bottles/time_sec*3600)
                break


class MonitoringLines:
    def __init__(self, session, users, db_bot) -> None:
        self.site_worker: SessionSite = session
        # all working regime
        self.working_lines: Dict[str, Line] = {}
        # line in gui
        self.tracking_lines: Dict[str, Line] = {}

        self.regimes_gui: list = settings.config.BASIC.REGIME
        self.regimes: list = settings.config.REPORTING.regime_for_report
        self.users: Dict[int, User] = users
        self.db_bot: Database = db_bot
        self.gui: Optional[Gui_app] = None
        self.last_intervening_entry: int = datetime.now().hour

    async def _get_mass_flow(self, item: Dict[str, str]) -> None:
        if item['mass_flow'] != 0:
            self.working_lines[item['lineName']].cont_txt_volume.bgcolor = '#FFEFD5'
        else:
            self.working_lines[item['lineName']].cont_txt_volume.bgcolor = ft.colors.WHITE

    async def _format_name_product(self, item) -> None:
        if item['full_name'] == '':
            self.working_lines[item['lineName']].name_product = 'УБП'
            self.working_lines[item['lineName']].txt_name_product.value = 'УБП'
            return

        if item['full_name'] != self.working_lines[item['lineName']].name_product:
            self.working_lines[item['lineName']].name_product = item['full_name']
            self.working_lines[item['lineName']].txt_name_product.value = item['full_name']

    @logger.catch
    async def _insert_line(self, item: Dict[str, str]) -> None:
        new_line = Line(
                        self.gui,
                        f'/lines/{item["pointOfControl"]}/details',
                        int(item['pointOfControl']),
                        item['lineName'],
                        item['full_name'],
                        item['regime'],
                        item['beg_time'],
                        self.users
                        )

        self.working_lines[item['lineName']] = new_line

        await self.get_data_line(new_line)
        await new_line.create_cl_line()
        await self._format_name_product(item)
        asyncio.create_task(new_line.write_history_regime(self.db_bot))

        if new_line.regime in self.regimes_gui:
            self.tracking_lines[item['lineName']] = new_line
            asyncio.create_task(self._update_active_lines(new_line, True))

    @logger.catch
    async def _del_line(self, item: Dict[str, str]) -> None:
        del_line = self.working_lines[item['lineName']]
        await del_line.update_history_regime(self.db_bot, item['beg_time'])

        if del_line.regime in self.regimes_gui:
            try:
                del self.tracking_lines[item['lineName']]
            except KeyError:
                pass
            asyncio.create_task(self._update_active_lines(del_line, False))

        del_line.is_work = False
        del self.working_lines[item['lineName']]

    async def _update_txt_info(self, line: Line) -> None:
        line.txt_volume.value = f"{line.alcovolume}"
        line.txt_bottles.value = f"{line.bottle_count} шт."

    @logger.catch
    async def _update_active_lines(self, line: Line, status: bool) -> None:
        # status == 1 - insert, 0 - delete
        if status:
            await self.gui.insert_line(line)
        else:
            await self.gui.del_line(line)
            if line.regime != 1:
                speed_line_h = await line.get_speed_line_total_db(self.db_bot)
                for tg_id, user in self.users.items():
                    if user.access['end_bottling']:
                        await send_completed_bottling(line, speed_line_h, tg_id)

    @logger.catch
    async def _check_counter_bottles(self, line: Line) -> None:
        # if line.bottle_count < counter_alerts
        # then suggest that you turn it on
        if (line.alcovolume > settings.config.BASIC.counter_alerts and
                line.bottle_count == 0):
            line.cont_txt_bottles.bgcolor = ft.colors.RED_300
        else:
            line.cont_txt_bottles.bgcolor = None

    async def get_regime_lines(self) -> str:
        response = await self.site_worker.execute_request('/lines')
        text = ''
        for item in response:
            if item['regime'] == 5:
                text += f"{item['lineName']}. Режим: {item['regime']} \n"
            else:
                text += f"<b>{item['lineName']}. Режим: {item['regime']}</b> &#10071; \n"
        return text

    @logger.catch
    async def _give_night_alerts(self, line_val: Dict[str, str]) -> None:
        for tg_id, user in self.users.items():
            if user.access['night_warning']:
                if user.night_alerts_count < 5:
                    user.night_alerts_count += 1
                    await send_night_warning(line_val, tg_id)
                else:
                    user.access['night_warning'] = 0
                    asyncio.create_task(user.update_night_alerts(datetime.now()))

    @logger.catch
    async def _input_volume_to_stop(self, line: Line) -> float | Literal['']:
        input_value = line.txtf_volume.value
        if input_value == '':
            return ''
        try:
            input_value = float(line.txtf_volume.value)
        except ValueError:
            await self.gui.get_msg_err('Введите число')
            # reset to the default value
            line.txtf_volume.value = ''
            line.volume_to_stop = ''
            input_value = ''
        return input_value

    @logger.catch
    async def _check_enable_alerts(self,
                                   input_value: float,
                                   line: Line) -> None:
        # if but_notify_on_off.data == False, and new input_value
        # then automatically turn on alerts if they are turned off
        # and in telegrams too
        if not line.but_notify_on_off.data:
            if input_value > line.alcovolume:
                await line.get_signal_active()
                for tg_id, notify in line.tg_notify.items():
                    if notify['is_on']:
                        line.tg_notify[tg_id]['count'] = 0

    @logger.catch
    async def _turn_on_warning_signal(self, line: Line) -> None:
        if line.signal_active == 1:
            self.gui.play_signal(line.name_line)
        for tg_id, notify in line.tg_notify.items():
            if notify['is_on']:
                if notify['count'] < 5:
                    notify['count'] += 1
                    asyncio.create_task(send_warning(line, tg_id))

    @logger.catch
    async def update_gui_regimes(self) -> None:
        if 1 in self.regimes_gui:
            self.regimes_gui.remove(1)
        else:
            self.regimes_gui.append(1)

        for name, line in self.working_lines.items():
            if line.regime not in self.regimes_gui:

                if name in self.tracking_lines.keys():
                    await self._update_active_lines(line, False)
                    self.tracking_lines.pop(name, None)
            else:
                if name not in self.tracking_lines.keys():
                    self.tracking_lines[name] = line
                    await self._update_active_lines(line, True)

    @logger.catch
    async def write_db_intervening_data(self) -> None:
        time = datetime.now()
        if time.minute == 0 and self.last_intervening_entry != time.hour:
            self.last_intervening_entry = time.hour
            async with self.db_bot.pool.acquire() as con:
                con: asyncpg.Connection
                for line in self.working_lines.values():
                    await con.execute(sql_query.insert_intervening_data,
                                      line.point_control,
                                      line.over_alko_volume + line.alcovolume,
                                      line.over_bottles_count + line.bottle_count)

    async def get_data_line(self, line: Line) -> None:
        response = await self.site_worker.execute_request(line.url_line)
        line.alcovolume = round(response['alko_volume'], 3)
        line.bottle_count = response['bottles_counts']

        line.over_alko_volume = response['over_alko_volume']
        line.over_bottles_count = response['over_bottles_counts']

    @logger.catch
    async def get_working_lines(self) -> None:
        response = await self.site_worker.execute_request('/lines')
        self.last_response_lines = response

        for item in response:
            # Выбираем новые работающие линии
            if (item['regime'] in self.regimes and
                    item['lineName'] not in self.working_lines.keys()):
                await self._insert_line(item)

            # Удаляем/обновляем данные
            if item['lineName'] in self.working_lines.keys():
                await self._get_mass_flow(item)
                await self._format_name_product(item)

                if (item['regime'] not in self.regimes
                    or
                    self.working_lines[item['lineName']].beg_time !=
                        datetime.strptime(item['beg_time'],
                                          '%Y-%m-%dT%H:%M:%SZ')):
                    await self._insert_line(item)

    @logger.catch
    async def check_line_limit(self) -> None:
        for line in self.working_lines.values():
            await self.get_data_line(line)
            await self._update_txt_info(line)
            await self._check_counter_bottles(line)

            input_value = await self._input_volume_to_stop(line)
            if input_value == '':
                continue

            # If the input value is != volume to stop, then we record it
            # and skip it until the next iteration
            # so that there are no accidental triggers
            if input_value != line.volume_to_stop:
                line.volume_to_stop = input_value
                await self._check_enable_alerts(input_value, line)
                continue

            if line.alcovolume >= line.volume_to_stop:
                await self._turn_on_warning_signal(line)

    @logger.catch
    async def check_night_alerts(self) -> None:
        if not settings.config.BASIC.NIGHT_ALERTS:
            return

        # Night alerts for open lines
        if datetime.now().hour < settings.config.BASIC.NIGHT_TIME_HOUR:
            return

        for line_val in self.last_response_lines:
            if line_val['regime'] == 5:
                continue
            asyncio.create_task(self._give_night_alerts(line_val))

    async def collection_interv_data(self) -> Never:
        period = 600
        while True:
            for line in self.tracking_lines.values():
                line.interv_data.append({'bottle_count': line.bottle_count,
                                         'create_time': datetime.now()})
                if len(line.interv_data) > 10:
                    line.interv_data.pop(0)
                await line.get_speed_line_per_10m(period)
                await line.get_speed_line_per_h()
                total_speed = await line.get_speed_line_total_now()

                line.txt_speed_line.value = f"{line.average_speed_10m} в час."
                line.txt_speed_line.tooltip = \
                    f"За час: {line.average_speed_h} в час\nВсего: {total_speed} в час"

                self.gui.update()

            await asyncio.sleep(period)

    async def processing_new_data(self) -> Never:
        asyncio.create_task(self.collection_interv_data())
        while True:
            await self.get_working_lines()
            await self.check_line_limit()
            await self.check_night_alerts()
            asyncio.create_task(self.write_db_intervening_data())

            self.gui.page.update()
            await asyncio.sleep(8)
