import threading

import ui
import alerts

import win32api
import msvcrt

import time

import savedata

import atexit

import tkinter
import tkinter.messagebox

import ctypes

import win32gui

# Call the function to unfocus the window

# tk = tkinter.Tk()

# tkinter.messagebox.showinfo("Due Alert", f"The assignment \"poopy\" should have been completed by now.")
"""
time.sleep(1)
tk.update_idletasks()

toplist = []
winlist = []
def enum_callback(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

win32gui.EnumWindows(enum_callback, toplist)
firefox = []
for hwnd, title in winlist:
    print(title)
firefox = [(hwnd, title) for hwnd, title in winlist if 'due' in title.lower()]
# just grab the first window that matches
firefox = firefox[0]
# use the window handle to set focus
win32gui.SetForegroundWindow(firefox[0])
"""

# tk.withdraw()

if __name__ == "__main__":
    atexit.register(savedata.save_all)
    savedata.load_all()

    # Start the assignment checking thread
    ui_thread = threading.Thread(target=ui.ui, daemon=True)
    ui_thread.start()

    # Continue with your UI code or other components
    alerts.check_assignments(ui_thread)
