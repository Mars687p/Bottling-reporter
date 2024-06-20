from datetime import datetime
from typing import TYPE_CHECKING, Dict

import flet as ft
from openpyxl import Workbook

from app.lines import IntervData
from app.logs import logger
from app.reporter.excel import ExcelWorkbook
from app.reporter.period_worker import ReportLinePerDate, TimePeriod
from templates import sql_query

if TYPE_CHECKING:
    from app.database import Database, asyncpg


class ReportingForm(ft.UserControl):
    def __init__(self, page: ft.Page, db: 'Database'):
        super().__init__()
        self.page = page
        self.db = db
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
        self.consider_flash = ft.Checkbox('Учитывать промывку?',
                                          value=True)
        self.consider_saturday = ft.Checkbox('Суббота - сверхурочно?',
                                             value=False)
        self.cl_time_periods: ft.Column = ft.Column()
        self.time_periods: Dict[int, TimePeriod] = {}
        self.period_serial: int = 0

    def build(self) -> ft.Container:
        self.page.window_min_width = 1280
        self.page.title = 'Bottling Reporter: Отчетность'

        self.page.scroll = ft.ScrollMode.ADAPTIVE

        self.page.theme = ft.Theme(color_scheme=ft.ColorScheme(
                                primary=ft.colors.GREEN,
                                primary_container=ft.colors.GREEN_200)
                    )
        self.page.bgcolor = '#FAFAD2'

        return ft.Container(ft.Text('Фильтрация данных',
                                    text_align=ft.TextAlign.CENTER,
                                    size=30,
                                    weight=ft.FontWeight.BOLD),
                            alignment=ft.alignment.center)

    async def init_app(self) -> None:
        self.content = ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                              expand=True,
                              wrap=True)
        self.preload.open = False
        await self.show_filters_form()

        self.page.update()

    async def show_preload(self) -> None:
        self.page.dialog = self.preload
        self.preload.open = True
        self.page.update()

    @logger.catch
    async def show_pick_line(self) -> ft.Container:
        self.lines = await self.db.select_sql(sql_query.select_lines)
        self.lines = {item['point_control']: item['line_name'] for item in self.lines}
        head_line = ft.Container(ft.Text('Выберите линии',
                                         text_align=ft.TextAlign.CENTER,
                                         size=20,
                                         weight=ft.FontWeight.BOLD),
                                 border=ft.border.only(
                                                    bottom=ft.BorderSide(2,
                                                                         ft.colors.BLACK)),
                                 bgcolor=ft.colors.GREY_100,
                                 border_radius=ft.border_radius.vertical(top=10),
                                 alignment=ft.alignment.center
                                 )
        self.chckbox_line = []
        for line_id, name in self.lines.items():
            chck = ft.Checkbox(name, data=line_id, value=True)
            self.chckbox_line.append(chck)

        cl_line = ft.Column(controls=[
                                head_line,
                                *self.chckbox_line,
                                     ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.START,
                            spacing=0
                            )
        cont_pick_line = ft.Container(
                            cl_line,
                            bgcolor='#F0FFF0',
                            border=ft.border.all(2, ft.colors.BLACK),
                            border_radius=ft.border_radius.all(10),
                            padding=0,)
        return cont_pick_line

    @logger.catch
    async def get_row_work_time(self) -> None:
        time_period = TimePeriod(self.page, self.period_serial)
        row_work_time = await time_period.get_gui_row(self.del_work_time)
        self.time_periods[self.period_serial] = time_period

        self.cl_time_periods.controls.append(row_work_time)
        self.period_serial += 1

    async def add_work_time(self, e: ft.ControlEvent) -> None:
        await self.get_row_work_time()
        self.page.update()

    @logger.catch
    async def del_work_time(self, e: ft.ControlEvent) -> None:
        self.cl_time_periods.controls.remove(self.time_periods[
                                            e.control.data].row_work_time)
        self.time_periods.pop(e.control.data)
        self.page.update()

    async def get_count_date(self) -> int:
        return sum(map(lambda pr: len(pr.data_per_dates),
                       self.time_periods.values()))

    async def form_work_time(self) -> ft.Container:
        head_period_time = ft.Container(
                                ft.Text('Периоды',
                                        text_align=ft.TextAlign.CENTER,
                                        size=20,
                                        weight=ft.FontWeight.BOLD),
                                border=ft.border.only(
                                                bottom=ft.BorderSide(2,
                                                                     ft.colors.BLACK)),
                                bgcolor=ft.colors.GREY_100,
                                border_radius=ft.border_radius.vertical(top=10),
                                alignment=ft.alignment.center
                        )
        but_add_period = ft.IconButton(icon=ft.icons.ADD, on_click=self.add_work_time)

        cl_work_time = ft.Column(controls=[
                                        head_period_time,
                                        self.cl_time_periods,
                                        but_add_period
                                        ],
                                 alignment=ft.MainAxisAlignment.START,)

        cont_work_time = ft.Container(
                                cl_work_time,
                                bgcolor='#F0FFF0',
                                border=ft.border.all(2, ft.colors.BLACK),
                                border_radius=ft.border_radius.all(10),
                                padding=ft.padding.only(bottom=10))
        return cont_work_time

    async def show_filters_form(self) -> None:
        self.content.controls.append(await self.show_pick_line())
        await self.get_row_work_time()
        self.content.controls.append(await self.form_work_time())

        self.content.controls.append(self.consider_saturday)
        self.content.controls.append(self.consider_flash)
        but_generate_report = ft.ElevatedButton('Сформировать отчет',
                                                on_click=self.generate_report)
        self.content.controls.append(but_generate_report)
        self.page.add(self.content)

    def _get_point_control(self) -> list[int]:
        point_control = []
        for chckbox in self.chckbox_line:
            if not chckbox.value:
                continue
            point_control.append(chckbox.data)
        return point_control

    def _get_query_select_regimes(self) -> str:
        if self.consider_flash.value:
            select_regimes = sql_query.select_regimes_per_period
        else:
            build_sql = sql_query.select_regimes_per_period.split('ORDER')
            build_sql.insert(1, f" AND {sql_query.not_consider_flash} ORDER")
            select_regimes = ''.join(build_sql)
        return select_regimes

    async def _processing_period(self,
                                 db_data: list,
                                 period: TimePeriod,
                                 con: 'asyncpg.Connection') -> None:
        for row in db_data:
            if period.data_per_dates.get(row['beg_time'].date()) is None:
                period.data_per_dates[row['beg_time'].date()] = {}
                per_date = period.data_per_dates[row['beg_time'].date()]
            else:
                per_date = period.data_per_dates[row['beg_time'].date()]

            if per_date.get(row['line_id']) is None:
                per_date[row['line_id']] = ReportLinePerDate(
                                            line_id=row['line_id'],
                                            line_name=self.lines[row['line_id']],
                                            date_day=row['beg_time'].date(),
                                            end_time=period.end_time,
                                            consider_saturday=self.consider_saturday.value
                                            )
            line_per_date = per_date[row['line_id']]
            line_per_date.history.append(row)

            if row['end_time'].time() > period.end_time:
                if line_per_date.interv_data is None:
                    d_t = datetime(
                                row['end_time'].year, row['end_time'].month,
                                row['end_time'].day,
                                period.end_time.hour,
                                period.end_time.minute)
                    d_t_end = datetime(
                                row['end_time'].year,
                                row['end_time'].month,
                                row['end_time'].day+1,
                                0, 0)

                    row = await con.fetchrow(sql_query.select_interv_data,
                                             row['line_id'],
                                             d_t,
                                             d_t_end)
                    if row is not None:
                        line_per_date.interv_data = IntervData(row)

    @logger.catch
    async def generate_report(self, e: ft.ControlEvent) -> None:
        await self.show_preload()
        point_control = self._get_point_control()
        select_regimes = self._get_query_select_regimes()

        async with self.db.pool.acquire() as con:
            con: asyncpg.Connection  # type: ignore
            for period in self.time_periods.values():
                period.data_per_dates = {}
                not_closed_regime = await con.fetch(
                                            sql_query.select_not_closed_regimes,
                                            period.start_date,
                                            period.end_date,
                                                    )
                if len(not_closed_regime) > 0:
                    period.calculate_err.append(
                                f'Не закрытые режимы в период с {period.start_date}'
                                f'по {period.end_date}')
                db_data = await con.fetch(
                                        select_regimes,
                                        period.start_date,
                                        period.end_date,
                                        point_control)
                await self._processing_period(db_data, period, con)

        wb_xlsx = ExcelWorkbook()
        count_date = await self.get_count_date()
        wb = await wb_xlsx.write_wb(self.time_periods, count_date)

        await self.save_report(wb, "Отчет об обьемах производства.xlsx")
        self.preload.open = False
        self.page.update()

    @logger.catch
    async def save_report(self, wb: Workbook, name: str) -> None:
        async def saver(e: ft.FilePickerResultEvent) -> None:
            try:
                if file_dialog.result.path is None:
                    return
                wb.save(file_dialog.result.path)
            except PermissionError:
                bar = ft.SnackBar(
                            content=ft.Text('Файл занят другим процессом',
                                            color=ft.colors.BLACK,
                                            size=36),
                            show_close_icon=True,
                            close_icon_color=ft.colors.RED, duration=10000,
                            bgcolor=ft.colors.YELLOW)
                self.page.snack_bar = bar
                bar.open = True
                return

        file_dialog = ft.FilePicker(on_result=saver)
        self.page.overlay.append(file_dialog)
        self.page.add(file_dialog)
        await file_dialog.save_file_async(
                                file_name=name,
                                file_type=ft.FilePickerFileType.CUSTOM,
                                allowed_extensions=['xlsx'])
