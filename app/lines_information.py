import requests, configparser
from time import sleep
from ast import literal_eval
from tkinter import *
from pygame import mixer
from app.Configuration import get_name_signal, get_url_site
from app.logs import logger
base_url = get_url_site()

class Line:
    def __init__(self, session, line, volume_to_stop = 9999, signal = 1):
        self.session = session
        self.url_line = line[0]
        self.name_line = line[1]
        self.name_product = line[2]
        self.volume_to_stop = volume_to_stop
        self.signal_active = signal
        self.elements_gui = [Label(text=self.name_line, font=('Arial', 18), padx=20, pady=5, bg='#ADFF2F'),
                             Label(text=self.get_alko_volume(), font=('Arial', 16), padx=20, pady=5, bg='#FFFACD'),
                             Entry(width=20, justify=CENTER, font=('Arial', 16)),
                             Button(text='Отключить оповещение', command=self.get_signal_active, font=('Arial', 16), width=10, height=1, padx=10, bg='#708090')]
        
    def get_alko_volume(self):
        return round(literal_eval(self.session.get(self.url_line).text)['alko_volume'], 3)

    def get_n_bottles(self):
        return literal_eval(self.session.get(self.url_line).text)['bottles_counts']

    def get_signal_active(self):
        self.signal_active *= -1
        if self.signal_active == 1: 
            self.elements_gui[3].configure(text='Отключить оповещение')
            self.elements_gui[3].configure(bg='#708090')
        else: 
            self.elements_gui[3].configure(text='Включить оповещение')
            self.elements_gui[3].configure(bg='red')
    
def signal(name_line, signal_active):
    audio_file = get_name_signal(name_line)
    mixer.init()
    mixer.music.load(audio_file)
    if signal_active == 1:
        mixer.music.play(2)
    else: 
        mixer.music.stop()


def get_working_lines(session=requests.Session(), working_lines=[]):
    url = base_url + 'lines'
    response = literal_eval(session.get(url).text)
    lst_line_name = [i.name_line for i in working_lines]
    tracking_changes = 0
    for item in response:
        # Выбираем новые работающие линии
        if item['regime'] in [4, 7, 9] and item['lineName'] not in lst_line_name:
            working_lines.append(Line(session, [f'{url}/{item["pointOfControl"]}/details', item['lineName'], item['full_name']]))
            tracking_changes = 1
        # Удаляем закрытые линии
        if item['regime'] not in [4, 7, 9] and item['lineName'] in lst_line_name:
            for index, line in enumerate(working_lines):
                if item['lineName'] == line.name_line: 
                    del working_lines[index]  
                    tracking_changes = 1
    return working_lines, tracking_changes

def get_regime_lines(session):
    url = base_url + 'lines'
    response = literal_eval(session.get(url).text)
    text = ''
    for item in response:
        if item['regime'] == 5: text += f"{item['lineName']}. Режим: {item['regime']} \n"
        else: text += f"*{item['lineName']}. Режим: {item['regime']}* \n"
    return text
    