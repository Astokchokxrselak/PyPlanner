import threading

import ui
import alerts

import win32api
import savedata

import atexit

if __name__ == "__main__":
    atexit.register(savedata.save_all)
    savedata.load_all()

    # Start the assignment checking thread
    ui_thread = threading.Thread(target=ui.ui, daemon=True)
    ui_thread.start()

    # Continue with your UI code or other components
    alerts.check_assignments(ui_thread)
