import win10toast
import win32api

import datetime
import time

from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)


def now(): return datetime.datetime.now()

alert_now = False
alert_name = ""
alert_desc = ""

def alert_due(assignment: BaseAssignment):
    # win32api.MessageBeep(0x00000040)
    print("we reach")

    win32api.MessageBox(0,
                        "The {0} \"{1}\" is due right now. Change the due date if you believe this is a mistake.".format(
                            "assignment", "Black Plague"), "Alert")

    # win32api.MessageBox(0,
    #                    "The {0} \"{1}\" is due right now. Change the due date if you believe this is a mistake.".format(
    #                        assignment.type, assignment.name), "Assignment Due Now", 0)


def alert_start(assignment: BaseAssignment):
    toaster = win10toast.ToastNotifier()
    toaster.show_toast("Random Alert",
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
def check_assignments():
    while True:
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
        time.sleep(ASSIGNMENT_CHECK_INTERVAL)  # Simulate the time taken for checking assignments
