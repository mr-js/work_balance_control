from playsound import *
import tkinter
from tkinter import *
import tkinter as tk
from tkinter import ttk
import getpass
import sys
import os
import pyautogui
from time import sleep
import logging
import configparser


logging.basicConfig(handlers=[logging.FileHandler(os.path.join('work_balance_control.log'), 'w', 'utf-8')], level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d.%m.%y %H:%M:%S')
window = Tk(); caption = tk.StringVar(); message = tk.StringVar(); comment = tk.StringVar(); summary = tk.StringVar(); answer = tk.StringVar()
timer = None


class WBC:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('work_balance_control.ini')
        if not (config.has_section('COMMON') and config.has_section('NOTIFIERS') and config.has_section('SYSTEM')):
            logging.debug('Inactive settings in INI-file')
            sys.exit(1)
        if not os.path.isfile(config.get('NOTIFIERS', 'sound_relax_begin')) or not os.path.isfile(config.get('NOTIFIERS', 'sound_relax_end')):
            logging.debug('Check sound settings in INI-file')
            sys.exit(1)
        self.current_time = 1
        self.current_work_time = 1
        self.work_duration = config.getint('COMMON', 'work_duration')
        self.work_delta = config.getint('COMMON', 'work_delta')
        self.relax_duration = config.getint('COMMON', 'relax_duration')
        self.relax_delta = config.getint('COMMON', 'relax_delta')
        self.relax_warning = config.getint('COMMON', 'relax_warning')
        self.interrupt_pause = config.getint('COMMON', 'interrupt_pause')
        self.maximum_work_time = config.getint('COMMON', 'maximum_work_time')
        self.maximum_time = config.getint('COMMON', 'maximum_time')
        self.next_relax_time = config.getint('COMMON', 'work_duration')
        self.next_relax_duration = config.getint('COMMON', 'relax_duration')
        self.sound_relax_begin = config.get('NOTIFIERS', 'sound_relax_begin')
        self.sound_relax_end = config.get('NOTIFIERS', 'sound_relax_end')
        self.sound_relax_warning = config.get('NOTIFIERS', 'sound_relax_warning')
        self.force_lock = config.getboolean('SYSTEM', 'force_lock')
        self.fullscreen = config.getboolean('SYSTEM', 'fullscreen')
        self.topmost = config.getboolean('SYSTEM', 'topmost')
        ## 60 - 1 minute (default), 1 - 1 second (demo)
        self.timer_clock_cycle = config.getint('SYSTEM', 'timer_clock_cycle')
        ## 0 - working, 1 - relaxing, -1 - ending
        self.relax_state_code = 0
        self.timer_state_active = True


def window_build():
    global window
    window.attributes('-fullscreen', timer.fullscreen, '-topmost', timer.topmost); window.overrideredirect(1); window.title('Work balance control'); window.geometry('1280x720'); window['bg'] = 'black'
    answer.set(timer.interrupt_pause)
    base_font_size = int(10 * ((window.winfo_screenwidth()/(1920/100) + window.winfo_screenheight()/(1080/100)) / 2) / 100)
    default_style = ttk.Style(); default_style.configure('New.TButton', font=('Helvetica', base_font_size))
    txt_caption = Label(window, font=('Arial Bold', 3 * base_font_size), fg='red', bg='black', textvariable=caption); txt_caption.grid(column=0, row=0); txt_caption.place(relx = .01, rely = .01)
    txt_message = Label(window, font=('Arial Bold', base_font_size), fg='white', bg='black', textvariable=message); txt_message.grid(column=0, row=0); txt_message.place(relx = .02, rely = .32)
    txt_comment = Label(window, font=('Arial Bold', base_font_size), fg='green', bg='black', textvariable=comment); txt_comment.grid(column=0, row=0); txt_comment.place(relx = .02, rely = .48)
    txt = Entry(window, font = f'Helvetica {base_font_size} bold', textvariable=answer); txt.place(relx = .02, rely = .64, relwidth=.025, relheight=.06)
    btn = Button(window, text='Give me minutes to finish my work', command=window_clicked); btn.place(relx = .05, rely = .64, relwidth=.2, relheight=.06)
    txt_summary = Label(window, font=('Arial Bold', base_font_size), fg='white', bg='black', textvariable=summary); txt_summary.grid(column=0, row=0); txt_summary.place(relx = .02, rely = .80)


def window_block():
    pyautogui.moveTo(x=680,y=800)
    window.protocol('WM_DELETE_WINDOW', window_block)
    window.update()


def window_warning():
    pass
    playsound(timer.sound_relax_warning, False)
    pass


def window_hide():
    if window.state() == 'normal':
        playsound(timer.sound_relax_end, False)
        window.withdraw()


def window_show():
    window.update()
    if window.state() == 'withdrawn':
        playsound(timer.sound_relax_begin, False)
        window.deiconify()


def window_clicked():
    logging.debug(f'control_interrupted: pause duration {timer.interrupt_pause}')
    timer.interrupt_pause = int(answer.get())
    window_hide()
    sleep(timer.timer_clock_cycle * timer.interrupt_pause)
    window_show()


def window_control_task():
    logging.debug(f'current time {timer.current_time}, current work time {timer.current_work_time}, next relax time {timer.next_relax_time}, next relax duration {timer.next_relax_duration}')
    summary.set(f'Time statistics: {timer.current_time} minutes / {timer.current_work_time} minutes / {timer.current_time - timer.current_work_time} minutes (total/work/rest)')
    if timer.relax_warning != 0:
        ## total working time warning
        if timer.current_time == timer.maximum_time  - timer.relax_warning or timer.current_work_time == timer.maximum_work_time - timer.relax_warning:
            logging.debug('total working time warning')
            window_warning()
        ## current working time warning
        if timer.current_time == timer.next_relax_time - timer.relax_warning:
            logging.debug('current working time warning')
            window_warning()
    ## total working time limit
    if timer.current_time >= timer.maximum_time or timer.current_work_time == timer.maximum_work_time:
        logging.debug('total working time limit')
        timer.relax_state_code = -1
    ## current working time limit
    elif timer.current_time == timer.next_relax_time:
        logging.debug('current working time limit')
        timer.relax_state_code = 1
    ## current relaxing time limit
    elif timer.current_time == timer.next_relax_time + timer.next_relax_duration:
        logging.debug('current relaxing time limit')
        timer.relax_state_code = 0
        timer.next_relax_time = timer.current_time + timer.work_duration + timer.work_delta
        timer.next_relax_duration += timer.relax_delta
    else:
        pass
    ## -1 state code - ending
    if timer.relax_state_code == -1:
        timer_state_active = False
        logging.info('ending')
        caption.set('Time to finish the work')
        message.set('Please finish your work. Work balance control')
        comment.set('Time to shut down the PC')
        window_show()
    ## 1 state code - relaxing
    elif timer.relax_state_code == 1:
        timer_state_active = True
        logging.info('relaxing')
        caption.set('Time to rest')
        message.set('Please take a break and rest. Work balance control')
        comment.set(f'Time to rest {timer.next_relax_time + timer.next_relax_duration - timer.current_time} minutes')
        window_show()
    ## 0 state code - working
    elif timer.relax_state_code == 0:
        timer_state_active = True
        logging.info('working')
        timer.current_work_time += 1
        caption.set('Time to start the work')
        message.set('Work hard, don\'t get distracted. Work balance control')
        comment.set(f'Working time {timer.next_relax_time + timer.next_relax_duration - timer.current_time} minutes')
        window_hide()
    else:
        pass
    if timer_state_active:
        timer.current_time += 1
        window.after(1000 * timer.timer_clock_cycle, window_control_task)
    else:
        pass


def main():
    global timer
    timer = WBC()
    window_build()
    window_hide()
    if timer.force_lock:
        window_block()
    window.after(1000 * timer.timer_clock_cycle, window_control_task)
    window.mainloop()


if __name__ == "__main__":
    main()
