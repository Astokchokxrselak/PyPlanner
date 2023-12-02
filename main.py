import threading

import ui
import alerts

import win32api

if __name__ == "__main__":
    win32api.MessageBox(0,
                        "The {0} \"{1}\" is due right now. Change the due date if you believe this is a mistake.".format(
                            "assignment", "Black ue"), "Alert")

    # Start the assignment checking thread
    assignment_thread = threading.Thread(target=alerts.check_assignments, daemon=True)
    assignment_thread.start()

    # Continue with your UI code or other components
    ui.ui()
