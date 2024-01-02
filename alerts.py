import win32api
import win10toast

import random
import datetime
import time

import ui
from tts import TTS
from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)

import tkinter
import tkinter.messagebox

import pyautogui
import time

import win32api

import ctypes

import msvcrt

import threading
from threading import Thread

from tkinter.messagebox import showinfo, showwarning
import tkinter as tk
import os

from typing import Callable

import asyncio


normal_tts = None
random_tts = None


def say_normal(what: str):
    global normal_tts

    voice = ui.state(ui.VALRT)
    if not normal_tts:
        normal_tts = TTS(voice)

    normal_tts.set_voice(voice)
    thread = Thread(target=lambda: normal_tts.say(what))
    thread.start()


def say_random(what: str):
    global random_tts

    voice = ui.state(ui.VRALR)
    if not random_tts:
        random_tts = TTS(voice)

    random_tts.set_voice(voice)
    thread = Thread(target=lambda: random_tts.say(what))
    thread.start()


def warn(title: str, say: Callable, description: str, voice='valrt'):
    try:
        root = tk.Tk()
        say(description)
        showwarning(title, description)
        root.destroy()
    except:  # idk
        pass


def info(title: str, say: Callable, description: str, voice='valrt'):
    try:
        root = tk.Tk()
        say(description)
        showinfo(title, description)
        root.destroy()
    except:  # idk
        pass


def unfocus_window():
    win32api.keybd_event(0x5B, 0)
    win32api.keybd_event(0x44, 0)
    win32api.keybd_event(0x5B, 0, 2)
    win32api.keybd_event(0x44, 0, 2)
    """
    # Get the screen width and height
    screen_width, screen_height = pyautogui.size()

    pyautogui.FAILSAFE = False
    # Move the mouse cursor to a location outside the screen
    pyautogui.moveTo(screen_width + 10, screen_height + 10)
    pyautogui.click(screen_width + 10, screen_height + 10)
    pyautogui.FAILSAFE = True

    # Optional: Add a small delay to make sure the mouse cursor has moved
    time.sleep(0.1)
    """

def now(): return datetime.datetime.now()


def enabled():
    return ui.is_trigger(ui.ALRON)


def alert_due(assignment: BaseAssignment):
    # win32api.MessageBeep(0x00000040)
    # print("we reach")
    if not enabled():
        return

    warn("Assignment Due", say_normal, f"The {assignment.type} {assignment.name} is due now.")

    # unfocus_window()
    # time.sleep(0.3)
    # tkinter.messagebox.showwarning("Due Alert", f"The {assignment.type} \"{assignment.name}\" should have been completed by now.")

    # tk.update_idletasks()

    # tkinter.messagebox.showinfo('Yo skrill drop it hard!', 'bwowowowowowowowowow')


# alert_due(BaseAssignment("Clid", "Cla", None, None, None, "assignment"))
# alert_due(BaseAssignment("Clid", "Cla", None, None, None, "assignment"))
# tk.mainloop()


def alert_start(assignment: BaseAssignment):
    if not enabled():
        return

    info("Assignment to be Started", say_normal, f"You should begin {assignment.type} {assignment.name} now.")
    # toaster = win10toast.ToastNotifier()
    # toaster.show_toast("Random Alert",
    #                    "This is an alert reminding you to begin the {0} \"{1}\" if you are not already in the process of doing so.".format(
    #                        assignment.type, assignment.name),
    #                   "alert.ico")
    time.sleep(2)
    # tkinter.messagebox.showinfo("Start Alert", f"You should start the {assignment.type} \"{assignment.name}\" now.")


ASSIGNMENT_CHECK_INTERVAL = 1
alert_cache = {
    # 'assgn.': (x, y) # x = time since start announce, y = time since due date announce
    # 'a': (-1, -1) # note
    # 'b': (0, -1) # start announce only
    # 'c': (-1, 0) # due announce only
    # 'd': (0, 0) # normal assignment
}


def clear_cache():
    global alert_cache
    alert_cache = {}


INDEXOF_START, INDEXOF_DUE = range(2)


def check_group_cache(g: Group):
    for a in g.in_progress:
        if not enabled():
            break
        assignment: BaseAssignment = a
        if assignment not in alert_cache:
            alert_cache[assignment] = [True, True]


def check_group_start_dates(g: Group):
    for a in g.in_progress:
        if not enabled():
            break
        assignment: BaseAssignment = a
        time_to_start = assignment.time_to_start_date()
        if alert_cache[assignment][INDEXOF_START] != 0 and time_to_start == 0:
            if assignment.is_persistent and not assignment.has_due_date:
                assignment.invoke_persistence()
            alert_start(assignment)
        alert_cache[assignment][0] = assignment.time_to_start_date()


def check_group_due_dates(g: Group):
    for a in g.in_progress:
        if not enabled():
            break
        assignment: BaseAssignment = a
        time_to_due = assignment.time_to_due_date()
        if alert_cache[assignment][INDEXOF_DUE] != 0 and time_to_due == 0:
            if assignment.is_persistent:
                assignment.invoke_persistence()
            alert_due(assignment)
            # g.in_progress.remove(assignment)
            # g.completed.append(assignment)
        alert_cache[assignment][1] = assignment.time_to_due_date()



POST_ERROR_PAUSE = 5
def check_assignments(ui_thread):
    while True:
        if not ui_thread.is_alive():
            break
        random_alert_check()
        # Check assignments and display alerts as needed
        for g in active_groups():
            check_group_cache(g)
            check_group_start_dates(g)
            check_group_due_dates(g)
        time.sleep(ASSIGNMENT_CHECK_INTERVAL)  # Simulate the time taken for checking assignments


random_alert_next_time = None
min_rand_interval, max_rand_interval = 7 * 60, 12 * 60


# TODO: offer the ability to do random alerts for:
#       any assignment
#       assignments that are due within a certain time
#       assignments that are currently being worked on


# TODO: offer the ability to enable random alerts for
#       specific groups and to disable random alerts
#       for specific assignments

#  atm: only supports assignments that are currently being worked on
#       only works for currently focused group
def random_alert():
    current_assignments = ui.get_focused_group().get_current_assignments()
    selected: BaseAssignment = random.choice(current_assignments)
    message = (f"This is a random alert reminding you to complete the {selected.type} {selected.name} "
               f"if you are not already in the process of doing so.")
    info("Random Alert", say_random, "Hello. " + message, ui.VRALR)


def random_alert_check():
    global random_alert_next_time

    time = datetime.datetime.now()
    if random_alert_next_time:
        if time > random_alert_next_time and ui.get_focused_group().any_current_assignments():
            random_alert()
            random_alert_next_time = None
    if not random_alert_next_time:
        random_alert_next_time = time + datetime.timedelta(seconds=random.randint(min_rand_interval, max_rand_interval))
