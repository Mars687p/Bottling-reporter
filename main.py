import sys
from datetime import datetime
from threading import Thread

from app.GUI import GUI
from app.Authorization import pass_authorization
from app.lines_information import *
from app.logs import logger

s = pass_authorization()

@logger.catch(onerror=lambda _: gui.exception_handing())
def check_line_limit(working_lines):
    from app.Bot import send_msg
    while True:
        working_lines = get_working_lines(s, working_lines[0])
        if working_lines[1]: gui.redrawing(working_lines[0])
        log = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        for line in working_lines[0]:      
            line.elements_gui[1]['text'] = line.get_alko_volume()

            if line.elements_gui[0]['text'] == line.name_line and line.elements_gui[2].get() != '': 
                try:
                    line.volume_to_stop = int(line.elements_gui[2].get())
                except Exception:
                    gui.get_msgbox()
                    line.elements_gui[2].delete(0, END)

            if line.get_alko_volume() >= line.volume_to_stop: 
                signal(line.name_line, line.signal_active)
                if gui.telegramID1.get(): send_msg(line, 0)
                if gui.telegramID2.get(): send_msg(line, 1)

        gui.lbl_log['text'] = log
        gui.window.update_idletasks()
        sleep(10)

def working_lines_for_bot(): return get_working_lines(s)[0]
def regime_lines_for_bot(): return get_regime_lines(s)


if __name__ == '__main__':
    gui = GUI()
    working_lines = get_working_lines(s) 

    from app.Bot import start_bot
    th_bot = Thread(target=start_bot, daemon=True)
    th_check_limit = Thread(target=check_line_limit, args=[working_lines], daemon=True)
    
    th_check_limit.start()
    th_bot.start()
    gui.run(working_lines[0])
    
