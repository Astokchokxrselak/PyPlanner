import win10toast
import win32api

import datetime
import time
import ui


from structs import BaseAssignment, groups

def now(): return datetime.datetime.now()


def alert_due(assignment: ui.BaseAssignment):
    win32api.MessageBeep(0x00000040)
    win32api.MessageBox(None,
                        "The {0} \"{1}\" is due right now. Change the due date if you believe this is a mistake.".format(
                            assignment.type, assignment.name), "Alert", 0)


def alert_start(assignment: ui.BaseAssignment):
    toaster = win10toast.ToastNotifier()
    toaster.show_toast("Random Alert",
                       "This is an alert reminding you to begin the {0} \"{1}\" if you are not already in the process of doing so.".format(
                           assignment.type, assignment.name),
                       "alert.ico")


ASSIGNMENT_CHECK_INTERVAL = 1
def check_assignments():
    while True:
        # Check assignments and display alerts as needed
        for g in ui.active_groups():
            for a in g.in_progress:
                assignment: ui.BaseAssignment = a
                if assignment.has_start_date and assignment.time_to_start_date() <= 0:
                    alert_start(assignment)
                if assignment.has_due_date and assignment.time_to_due_date() <= 0:
                    alert_due(assignment)
                    g.in_progress.remove(assignment)
                    g.completed.append(assignment)
        time.sleep(ASSIGNMENT_CHECK_INTERVAL)  # Simulate the time taken for checking assignments
