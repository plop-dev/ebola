import pyautogui
import asyncio
import json
import base64
import websockets
import socketio

io = socketio.AsyncServer()

@io.event
async def connect():
    print('connection established')

# @io.event
# async def my_message(data):
#     print('message received with ', data)
#     await io.emit('my response', {'response': 'my response'})

@io.event
async def disconnect():
    print('disconnected from server')

async def send_screen_data(uri):
    await io.connect(uri, transports=['websocket'])
    
    # Capture the screen
    image = pyautogui.screenshot()

    # Convert the image to base64
    image_data = base64.b64encode(image.tobytes()).decode()

    await io.emit('screen-data', "hi just a test")

    # # Wait for 0.1 seconds
    # await asyncio.sleep(0.1)
    await io.wait()

if __name__ == "__main__":
    uri = "http://localhost:4101"
    asyncio.get_event_loop().run_until_complete(send_screen_data(uri))
