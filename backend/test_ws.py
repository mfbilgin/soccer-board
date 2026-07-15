import asyncio
import websockets
import sys

async def test():
    try:
        async with websockets.connect('ws://127.0.0.1:8000/api/multiplayer/ws?token=test') as ws:
            print("Connected!")
    except Exception as e:
        print("Error:", e)
        print("Type:", type(e))

asyncio.run(test())
