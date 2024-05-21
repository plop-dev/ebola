import keyboard

def log_key(event):
    print(event)

keyboard.on_press(log_key)
keyboard.wait('a')
