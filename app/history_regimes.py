import asyncio
import flet as ft


from datetime import datetime

from app.logs import logger
from templates import sql_query
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from app.database import Database, asyncpg


class HistoryForm(ft.UserControl):
    def __init__(self, page, db):
        super().__init__()
        self.page = page
        self.db: Database = db
        self.preload = ft.AlertDialog(modal=True,
                    content=ft.Column(
                    [ft.ProgressRing(), ft.Text('Пожалуйста подождите...')],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    height=150, 
                    ))
        self.history: list[asyncpg.Record] = []

    def build(self):
        self.page.window_min_width = 1280
        self.page.window_min_height = 600
        self.page.window_width = 1440
        self.page.title = 'Bottling Reporter: История режимов'

        self.page.scroll = ft.ScrollMode.ADAPTIVE

        self.page.theme = ft.Theme(color_scheme=ft.ColorScheme(
                                primary=ft.colors.GREEN,
                                primary_container=ft.colors.GREEN_200)
                    )
        self.page.bgcolor = '#FAFAD2'

        return ft.Container(ft.Text('История режимов', text_align=ft.TextAlign.CENTER, size=30, 
                                     weight=ft.FontWeight.BOLD),
                                     alignment=ft.alignment.center)

    async def init_app(self):
        self.content = ft.Row(alignment=ft.MainAxisAlignment.CENTER, expand=True, wrap=True)
        self.preload.open = False
        await self.show_history_form()

        self.page.update()

    async def show_preload(self):
        self.page.dialog = self.preload
        self.preload.open = True
        self.page.update()
    
    async def show_flash(self, e: Optional[ft.ControlEvent] = None): 
        await self.get_table_history()
        self.page.update()
    
    async def get_table_history(self):
        self.table_history.rows.clear()

        if not self.chck_flash.value:
            history = [i for i in self.history if i['regime'] != 1]
        else:
            history = self.history

        for index, regime in enumerate(history, 1):
            if not index % 2:
                color_row = {ft.MaterialState.DEFAULT: ft.colors.with_opacity(0.7, ft.colors.YELLOW_50),}
            else: 
                color_row = {ft.MaterialState.DEFAULT: ft.colors.WHITE70,}
            
            try:
                beg_time = f"{regime['beg_time'].date()} {regime['beg_time'].time()}"
                end_time = f"{regime['end_time'].date()} {regime['end_time'].time()}"
            except AttributeError:
                beg_time = ''
                end_time = ''

            self.table_history.rows.append(ft.DataRow(cells=
                                        [
                                            ft.DataCell(ft.Text(regime['line_id'], selectable=True, size=11)),
                                            ft.DataCell(ft.Text(regime['line_name'], selectable=True, size=11)),
                                            ft.DataCell(ft.Text(regime['product_name'], selectable=True, size=11)),
                                            ft.DataCell(ft.Text(regime['regime'], selectable=True, size=11)),
                                            ft.DataCell(ft.Text(regime['alko_volume'], selectable=True, size=11)),
                                            ft.DataCell(ft.Text(regime['bottles_count'], selectable=True, size=11)),
                                            ft.DataCell(ft.Text(beg_time, selectable=True, size=11)),
                                            ft.DataCell(ft.Text(end_time, selectable=True, size=11)),
                                        ],
                                    color=color_row
                                ))


    async def show_history_form(self):
        async with self.db.pool.acquire() as con:
            con: asyncpg.Connection
            self.history = await con.fetch(sql_query.select_history_regimes)

        self.table_history = ft.DataTable(columns=[
                                    ft.DataColumn(ft.Text('Точка учета')),
                                    ft.DataColumn(ft.Text('Линия розлива')),
                                    ft.DataColumn(ft.Text('Наименование продукта')),
                                    ft.DataColumn(ft.Text('Режим')),
                                    ft.DataColumn(ft.Text('Обьем')),
                                    ft.DataColumn(ft.Text('Бутылки')),
                                    ft.DataColumn(ft.Text('Дата начала')),
                                    ft.DataColumn(ft.Text('Дата окончания')),
                                    ],
                                        rows=[], 
                                        heading_row_color=ft.colors.BLACK12, 
                                        horizontal_lines=ft.border.BorderSide(1, "black"),
                                        vertical_lines=ft.border.BorderSide(1, "black"),
                                        show_bottom_border=True,
                                        bgcolor=ft.colors.WHITE, )

        self.chck_flash = ft.Checkbox('Показывать промывку', value=False, on_change=self.show_flash)    
        
        await self.get_table_history()
        self.content = ft.Column(
                            [
                            self.chck_flash, 
                            ft.Container(
                                ft.ListView([self.table_history]), 
                                height=550, bgcolor=ft.colors.WHITE,
                                border=ft.border.all(4, "black")
                                )
                            ]
        )

        self.page.add(self.content)
        self.page.update()