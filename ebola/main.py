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
import win32gui, win32ui
import sounddevice as sd
import soundfile as sf

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

SOCKET_PORT = 4101

working_dir = "."
_capture_screen = bool(False)

audio_on = False

AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
DURATION = 1

@sio.event
async def connect(sid, environ):
    global audio_on
    print('connect', sid)
    # get_admin()
    await sio.emit('command_dir', os.path.abspath(working_dir))
    audio_on = False

@sio.event
async def disconnect(sid):
    print('disconnect', sid)
    await stop_stream()
    
@sio.event
async def start_stream(_, res):
    global audio_on, _capture_screen
    
    print("start_stream with res:", res)
    _capture_screen = True
    # await capture_screen()
    asyncio.create_task(capture_screen(res))
    
    if audio_on:
        audio_thread = threading.Thread(target=asyncio.run, args=(stream_audio(),), daemon=True)
        audio_thread.start()
        # asyncio.create_task(stream_audio())

    
async def capture_screen(res):
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
            await asyncio.sleep(0.1)


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

def get_admin(*_):
    # Check if running with admin privileges
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    # Relaunch the script with admin privileges if needed
    def run_as_admin():
        print(is_admin())
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([str(arg) for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

    # Run the script with admin permissions
    run_as_admin()
    
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


if __name__ == '__main__':
    web.run_app(app=app, port=SOCKET_PORT)
