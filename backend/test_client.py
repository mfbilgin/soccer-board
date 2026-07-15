import asyncio
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/api/multiplayer/ws?token=test"
    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri) as ws:
            print("Successfully connected!")
            await ws.close()
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"Server rejected connection with status code: {e.status_code}")
    except Exception as e:
        print(f"Connection failed: {type(e).__name__} - {e}")

asyncio.run(test())
