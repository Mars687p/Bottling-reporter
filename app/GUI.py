import asyncio
from datetime import datetime
from multiprocessing import Process

import flet as ft
import toml
from pygame import mixer

from app.configuration import settings
from app.database import Database
from app.history_regimes import HistoryForm
from app.lines import Line, MonitoringLines
from app.reporting import ReportingForm
from bot.handlers.send_msg import send_calling_supervisor


class Gui_app(ft.Row):
    def __init__(self, page: ft.Page, monitor_lines: MonitoringLines):
        super().__init__()
        self.mixer = mixer
        self.page = page
        self.monitor_lines = monitor_lines
        self.monitor_lines.gui = self
        self.cont_close_line = ft.Container(
                                    ft.Text(
                                        'Нет открытых линий',
                                        size=28,
                                        expand=True,
                                        text_align=ft.TextAlign.CENTER,
                                        weight=ft.FontWeight.BOLD),
                                    visible=False,
                                    alignment=ft.alignment.center)
        self.preload = ft.AlertDialog(
                        modal=True,
                        content=ft.Column(
                                [ft.ProgressRing(),
                                    ft.Text('Пожалуйста подождите...')],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                height=150,
                                )
                    )
        self.txt_time = ft.Container(ft.Text(
                                            '',
                                            size=20,
                                            expand=True,
                                            text_align=ft.TextAlign.CENTER,
                                            weight=ft.FontWeight.BOLD),
                                     alignment=ft.alignment.center)

    def build(self) -> ft.Row:
        self.page.title = 'Bottling reporter'
        self.page.window_height = 200
        self.page.window_width = 400
        self.page.window_min_height = 190
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        self.page.on_window_event = self.window_event

        self.page.theme = ft.Theme(color_scheme=ft.ColorScheme(
                                primary=ft.colors.GREEN,
                                primary_container=ft.colors.GREEN_200)
                    )
        self.page.bgcolor = '#FAFAD2'

        self.but_upd_reg = ft.IconButton(ft.icons.WATER_DROP_OUTLINED,
                                         on_click=self.upd_regimes)
        self.but_night_al = ft.IconButton(ft.icons.NIGHTLIGHT_OUTLINED,
                                          on_click=self.on_off_night_alerts)
        self.but_report = ft.IconButton(ft.icons.REAL_ESTATE_AGENT_ROUNDED,
                                        on_click=self.open_reporter,
                                        tooltip='Отчет по розливу')
        self.but_history = ft.IconButton(ft.icons.HISTORY_TOGGLE_OFF_SHARP,
                                         on_click=self.open_history_regimes,
                                         tooltip='История режимов')
        self.but_call_visor = ft.IconButton(ft.icons.SOS_OUTLINED,
                                            on_click=self.call_visor,
                                            tooltip='SOS')
        appbar = ft.AppBar(
                        toolbar_height=40,
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLACK,
                        leading=self.but_upd_reg,
                        actions=[
                                self.but_history,
                                self.but_call_visor,
                                self.but_report,
                                self.but_night_al,
                                ]
        )

        self.page.appbar = appbar

        self.content = ft.Row(alignment=ft.MainAxisAlignment.CENTER, expand=True, wrap=True)
        return self.content

    async def init_app(self) -> None:
        self.preload.open = False

        asyncio.create_task(self.current_time())
        self.mixer.init()

        await self.get_el_night_alerts()
        await self.get_flash_regime()
        self.page.add(self.cont_close_line, self.txt_time)
        await self.check_open_lines()
        await self.get_size_window()
        self.page.update()

    async def call_visor(self, e: ft.ControlEvent) -> None:
        await send_calling_supervisor(f"{self.monitor_lines.users[1128438137].name}",
                                      1128438137)

    async def on_off_night_alerts(self, e: ft.ControlEvent) -> None:
        new_toml = toml.load(settings.path_file)
        if settings.config.BASIC.night_alerts:
            new_toml['Basic']['night_alerts'] = 0
        else:
            new_toml['Basic']['night_alerts'] = 1
        settings.update_settings(new_toml)
        await self.get_el_night_alerts()
        self.page.update()

    async def window_event(self, e: ft.ControlEvent) -> None:
        if e.data == 'restore':
            await asyncio.sleep(0.1)
            await self.get_size_window()
            self.page.update()

    async def get_el_night_alerts(self) -> None:
        if settings.config.BASIC.night_alerts:
            self.but_night_al.icon_color = ft.colors.BLUE
            self.but_night_al.tooltip = 'Ночные уведомления вкл.'
        else:
            self.but_night_al.icon_color = ft.colors.GREY
            self.but_night_al.tooltip = 'Ночные уведомления откл.'

    async def get_flash_regime(self) -> None:
        if 1 in self.monitor_lines.regimes_gui:
            self.but_upd_reg.icon_color = ft.colors.BLUE
            self.but_upd_reg.tooltip = 'Промывка отслеживается'
        else:
            self.but_upd_reg.icon_color = ft.colors.GREY
            self.but_upd_reg.tooltip = 'Промывка не отслеживается'

    async def upd_regimes(self, e: ft.ControlEvent) -> None:
        await self.monitor_lines.update_gui_regimes()
        await self.get_flash_regime()
        self.page.update()

    async def current_time(self) -> None:
        while True:
            self.txt_time.content.value = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            self.page.update()
            await asyncio.sleep(1)

    async def show_preload(self) -> None:
        self.page.dialog = self.preload
        self.preload.open = True
        self.page.update()

    def play_signal(self, name_line) -> None:
        audio_file = settings.config.AUDIO.get(name_line)
        self.mixer.music.load(audio_file)
        self.mixer.music.play()

    def stop_signal(self) -> None:
        self.mixer.music.stop()

    async def show_banner(self, msg: str, banner_type: str) -> None:
        # banner_type = err or info
        async def close_banner(e):
            self.page.banner.open = False
            self.page.update()

        self.page.banner = ft.Banner(
            leading=ft.Icon(ft.icons.INFO_OUTLINE_ROUNDED, color=ft.colors.BLUE, size=36),
            content=ft.Text(msg, size=28, color=ft.colors.BLACK),
            actions=[
                ft.ElevatedButton("Закрыть", on_click=close_banner),
            ],
        )

        if banner_type == 'err':
            self.page.banner.bgcolor = ft.colors.RED
        elif banner_type == 'info':
            self.page.banner.bgcolor = ft.colors.YELLOW_100

        self.page.banner.open = True
        self.page.update()

    async def get_msg_err(self, msg: str) -> None:
        async def close_dialog(e: ft.ControlEvent):
            dg.open = False
            self.page.update()

        dg = ft.AlertDialog(
                        content=ft.Text(msg),
                        actions=[ft.TextButton('Понятно', on_click=close_dialog, data=1)],
                        actions_alignment=ft.MainAxisAlignment.END,)

        self.page.dialog = dg
        dg.open = True
        self.page.update()

    async def check_open_lines(self) -> None:
        if len(self.content.controls) == 0:
            self.cont_close_line.visible = True
        else:
            self.cont_close_line.visible = False

    async def insert_line(self, line: Line) -> None:
        self.content.controls.append(line.gui_elements)
        await self.check_open_lines()
        await self.get_size_window()
        self.page.update()

    async def del_line(self, line: Line) -> None:
        for index, cl_line in enumerate(self.content.controls):
            if cl_line.data == line.name_line:
                self.content.controls.pop(index)
                await self.get_size_window()
                await self.check_open_lines()
                break
        self.page.update()

    async def get_size_window(self) -> None:
        try:
            width = self.content.controls[0].width
        except IndexError:
            self.page.window_min_width = 400

            self.page.window_width = 400
            self.page.window_height = 190
            return

        width += width * 0.12
        window_width = len(self.content.controls) * width

        self.page.window_min_width = width
        self.page.window_width = window_width

        line_name: str | None = None
        for name in self.monitor_lines.working_lines.keys():
            line_name = name
            break
        if line_name is not None:
            len_tg_swtich = len(
                self.monitor_lines.working_lines[line_name].switch_tg_notify) * 40
            self.page.window_height = 460 + len_tg_swtich

    """--------------------------------------------------------------------------------"""
    """---------------------------------NEW WINDOW-------------------------------------"""
    """--------------------------------------------------------------------------------"""

    async def open_reporter(self, e: ft.ControlEvent) -> None:
        reporter_module = Process(target=new_process_report, args=[])
        reporter_module.start()

    async def open_history_regimes(self, e: ft.ControlEvent) -> None:
        history_module = Process(target=new_process_history_regimes, args=[])
        history_module.start()


def new_process_report() -> None:
    async def window(page: ft.Page) -> None:
        try:
            db = Database('bottling_reporter_bot', 'bot')
            await db.get_connection()
            app = ReportingForm(page, db)
            page.add(app)
            await app.show_preload()
            await app.init_app()

            while True:
                await asyncio.sleep(3600)
        finally:
            await db.pool.close()
            print('db close')

    ft.app(target=window)


def new_process_history_regimes() -> None:
    async def window(page: ft.Page) -> None:
        try:
            db = Database('bottling_reporter_bot', 'bot')
            await db.get_connection()
            app = HistoryForm(page, db)
            page.add(app)
            await app.show_preload()
            await app.init_app()

            while True:
                await asyncio.sleep(3600)
        finally:
            await db.pool.close()
            print('db close')

    ft.app(target=window)
