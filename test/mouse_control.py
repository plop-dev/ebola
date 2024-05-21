import ctypes
from screeninfo import get_monitors

primary_monitor = None
for m in get_monitors():
    if m.is_primary:
        primary_monitor = m
        break

x = 0.9
y = 0.2
width = primary_monitor.width
height = primary_monitor.height

ctypes.windll.user32.SetCursorPos(int(width * x), int(height * y))
