import win32api
import win10toast

import datetime
import time

from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)

import tkinter
import tkinter.messagebox

import win32api
tk = tkinter.Tk()
tk.withdraw()  # hide tk...


def now(): return datetime.datetime.now()

alert_now = False
alert_name = ""
alert_desc = ""


def alert_due(assignment: BaseAssignment):
    # win32api.MessageBeep(0x00000040)
    # print("we reach")

    win32api.keybd_event(0x5B, 0, )  # LWIN
    win32api.keybd_event(0x44, 0, )  # D
    win32api.keybd_event(0x5B, 0, 2)
    win32api.keybd_event(0x44, 0, 2)

    time.sleep(0.2)
    tkinter.messagebox.showinfo("Due Alert", f"The {assignment.type} \"{assignment.name}\" should have been completed by now.")

#    toaster = win10toast.ToastNotifier()
#    toaster.show_toast("Random Alert",
#                       "This is an alert reminding you to begin the {0} \"{1}\" if you are not already in the process of doing so.".format(
#                           assignment.type, assignment.name),
#                       "alert.ico")
    # tkinter.messagebox.showinfo('Yo skrill drop it hard!', 'bwowowowowowowowowow')



def alert_start(assignment: BaseAssignment):
    toaster = win10toast.ToastNotifier()
    toaster.show_toast("Start Alert",
                       "This is an alert reminding you to begin the {0} \"{1}\" if you are not already in the process of doing so.".format(
                           assignment.type, assignment.name),
                       "alert.ico")


ASSIGNMENT_CHECK_INTERVAL = 1
alert_cache = {
    # 'assgn.': (x, y) # x = time since start announce, y = time since due date announce
    # 'a': (-1, -1) # note
    # 'b': (0, -1) # start announce only
    # 'c': (-1, 0) # due announce only
    # 'd': (0, 0) # normal assignment
}
INDEXOF_START, INDEXOF_DUE = range(2)


def check_assignments(ui_thread):
    while True:
        if not ui_thread.is_alive():
            break
        try:
            # Check assignments and display alerts as needed
            for g in active_groups():
                for a in g.in_progress:
                    assignment: BaseAssignment = a
                    time_to_start, time_to_due = assignment.time_to_start_date(), assignment.time_to_due_date()
                    if assignment not in alert_cache:
                        alert_cache[assignment] = [True, True]
                    if alert_cache[assignment][INDEXOF_START] != 0 and time_to_start == 0:
                        alert_start(assignment)
                    if alert_cache[assignment][INDEXOF_DUE] != 0 and time_to_due == 0:
                        alert_due(assignment)
                        # g.in_progress.remove(assignment)
                        # g.completed.append(assignment)
                    alert_cache[assignment] = [assignment.time_to_start_date(), assignment.time_to_due_date()]
        except:
            input("YOU FUCK!!!! GRRR!!!!!!!!!")
        time.sleep(ASSIGNMENT_CHECK_INTERVAL)  # Simulate the time taken for checking assignments
