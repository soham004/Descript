import pygetwindow as gw
import ctypes
# Allow the current process to set the foreground window
ctypes.windll.user32.AllowSetForegroundWindow(-1)
gw.getWindowsWithTitle("Warning:")[0].activate()