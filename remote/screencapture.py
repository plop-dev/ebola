import pyautogui
import asyncio
import socketio
import base64
from aiohttp import web
import mss

sio = socketio.AsyncServer(cors_allowed_origins="http://localhost:4100")
app = web.Application()
sio.attach(app)

SOCKET_PORT = 4101

# async def some_background_task():
#     await asyncio.sleep(10)
#     sio.emit('my event', data={'foo': 'bar'}, room='my room')

@sio.event
async def connect(sid, environ):
    print('connect ', sid)
    # asyncio.create_task(some_background_task())

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)
    
@sio.event
async def start_screen(*_):
    print("capture_screen")
    
    for _ in range(0, 50):
        with mss.mss() as sct:
            sct.compression_level = 1
            monitor = sct.monitors[1]  # or a region
            sct_img = sct.grab(monitor)
            
            png = mss.tools.to_png(sct_img.rgb, sct_img.size)
            png_data = base64.b64encode(png).decode()
            
            await sio.emit('screen-data', png_data)
            await asyncio.sleep(0.05)


if __name__ == '__main__':
    web.run_app(app=app, port=SOCKET_PORT)
