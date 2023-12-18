import win32api
import win10toast

import datetime
import time

import ui
from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)

import tkinter
import tkinter.messagebox

import pyautogui
import time

import win32api

import ctypes

import msvcrt

def unfocus_window():
    # Get the screen width and height
    screen_width, screen_height = pyautogui.size()

    pyautogui.FAILSAFE = False
    # Move the mouse cursor to a location outside the screen
    pyautogui.moveTo(screen_width + 10, screen_height + 10)
    pyautogui.click(screen_width + 10, screen_height + 10)
    pyautogui.FAILSAFE = True

    # Optional: Add a small delay to make sure the mouse cursor has moved
    time.sleep(0.1)

tk = tkinter.Tk()

def now(): return datetime.datetime.now()

def enabled():
    return True # ui.is_trigger(ui.ALRON)

def alert_due(assignment: BaseAssignment):
    # win32api.MessageBeep(0x00000040)
    # print("we reach")
    if not enabled():
        return

    tk.update_idletasks()
    tkinter.messagebox.showwarning("Due Alert", f"The assignment \"poopy\" should have been completed by now.")

#    toaster = win10toast.ToastNotifier()
#    toaster.show_toast("Random Alert",
#                       "This is an alert reminding you to begin the {0} \"{1}\" if you are not already in the process of doing so.".format(
#                           assignment.type, assignment.name),
#                       "alert.ico")
    # tkinter.messagebox.showinfo('Yo skrill drop it hard!', 'bwowowowowowowowowow')


# alert_due(BaseAssignment("Clid", "Cla", None, None, None, "assignment"))
# alert_due(BaseAssignment("Clid", "Cla", None, None, None, "assignment"))
# tk.mainloop()


def alert_start(assignment: BaseAssignment):
    if not enabled():
        return

    tkinter.messagebox.showinfo("Start Alert", f"The assignment \"poopy\" should have been completed by now.")


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


def check_assignments(ui_thread):
    while True:
        if not ui_thread.is_alive():
            break
        # Check assignments and display alerts as needed
        for g in active_groups():
            for a in g.in_progress:
                if a not in alert_cache:
                    alert_cache[a] = [True, True]
                if alert_cache[a][INDEXOF_DUE] != 0 and a.time_to_due_date() == 0:
                    alert_due(a)
                alert_cache[a] = [a.time_to_start_date(), a.time_to_due_date()]
                """if not enabled():
                    break
                assignment: BaseAssignment = a
                time_to_start, time_to_due = assignment.time_to_start_date(), assignment.time_to_due_date()
                if assignment not in alert_cache:
                    alert_cache[assignment] = [True, True]
                if alert_cache[assignment][INDEXOF_START] != 0 and time_to_start == 0:
                    alert_start(assignment)
                    if assignment.is_persistent and not assignment.has_due_date:
                        assignment.invoke_persistence()
                if alert_cache[assignment][INDEXOF_DUE] != 0 and time_to_due == 0:
                    alert_due(assignment)
                    if assignment.is_persistent:
                        assignment.invoke_persistence()
                    # g.in_progress.remove(assignment)
                    # g.completed.append(assignment)
                alert_cache[assignment] = [assignment.time_to_start_date(), assignment.time_to_due_date()]
                """
        time.sleep(ASSIGNMENT_CHECK_INTERVAL)  # Simulate the time taken for checking assignments
