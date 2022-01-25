import sys
from datetime import datetime
from tkinter import *
from tkinter import messagebox

from app.logs import logger


class GUI():
    def __init__(self):
        self.window = Tk()
        self.lbl_log = Label(text=f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', font=('Arial', 12), bg='#FFFACD')
        self.lbl_info = Label(text='Нет открытых линий', font=('Arial', 30), padx=10, pady=5, bg='#FFFACD')
        self.telegramID1 = IntVar()
        self.telegramID2 = IntVar()
        self.cb1 = Checkbutton(text='Оповещение Владимира', variable=self.telegramID1, font=('Arial', 12), bg='#FFFACD')
        self.cb2 = Checkbutton(text='Оповещение Сергея', variable=self.telegramID2, font=('Arial', 12), bg='#FFFACD')

    def run(self, lines):
        self.window.configure(bg='black')
        self.window.title('End if Bottling warning')
        self.window.resizable(False, False)
        if len(lines) == 0:
            self.lbl_info.grid(column=0, row = 0, sticky='nsew')
            self.lbl_log.grid(column=0, row = 1, sticky="nsew")
            self.window.mainloop()
            return
        
        for index_column, line in enumerate(lines):
            for index_row, element in enumerate(line.elements_gui):
                element.grid(column=index_column, row=index_row, padx=3, ipady=10, sticky="nsew")
                if index_row == 2 and line.volume_to_stop != 9999: element.insert(0, str(line.volume_to_stop))
        self.cb1.grid(column=0, row = index_row + 1, columnspan=index_column + 1, sticky="nsew")
        self.cb2.grid(column=0, row = index_row + 2, columnspan=index_column + 1, sticky="nsew")
        self.lbl_log.grid(column=0, row = index_row + 3, columnspan=index_column + 1, sticky="nsew")
        self.window.mainloop()

    def redrawing(self, lines):
        for widget in self.window.winfo_children():
            widget.grid_forget()
        
        if len(lines) == 0:
            self.lbl_info.grid(column=0, row = 0, sticky='nsew')
            self.lbl_log.grid(column=0, row = 1, sticky="nsew")
            self.window.update()  
            return

        for index_column, line in enumerate(lines):
            for index_row, element in enumerate(line.elements_gui):
                element.grid(column=index_column, row=index_row, padx=3, ipady=10, sticky="nsew")
        self.cb1.grid(column=0, row = index_row + 1, columnspan=index_column + 1, sticky="nsew")
        self.cb2.grid(column=0, row = index_row + 2, columnspan=index_column + 1, sticky="nsew")
        self.lbl_log.grid(column=0, row = index_row + 3, columnspan=index_column + 1, sticky="nsew")
        self.window.update()  

    def get_msgbox(self):
        messagebox.showerror(title='Ошибка', message='Введите целое число')

    def exception_handing(self):
        self.window.destroy()
        sys.exit(1)