import threading
import asyncio
import socketio
import base64
from aiohttp import web
import mss

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

SOCKET_PORT = 4101

_capture_screen = bool(False)

@sio.event
async def connect(sid, environ):
    print('connect ', sid)

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)
    await stop_stream()
    
@sio.event
async def start_stream(*_):
    print("start_stream")
    global _capture_screen
    _capture_screen = True
    await capture_screen()

    
async def capture_screen():
    while _capture_screen:
        with mss.mss() as sct:
            sct.compression_level = 1
            monitor = sct.monitors[1]  # or a region
            sct_img = sct.grab(monitor)
            
            png = mss.tools.to_png(sct_img.rgb, sct_img.size)
            png_data = base64.b64encode(png).decode()
            
            await sio.emit('stream-data', png_data)
            await asyncio.sleep(0.1)

@sio.event
async def stop_stream(*_):
    global _capture_screen
    _capture_screen = False
    print("stop_screen")


if __name__ == '__main__':
    web.run_app(app=app, port=SOCKET_PORT)
