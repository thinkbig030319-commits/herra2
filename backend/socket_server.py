import socketio
import asyncio
from .monitor import get_system_stats

sio = socketio.AsyncServer(async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print("Client Connected:", sid)

async def broadcast():
    while True:
        stats = get_system_stats()
        await sio.emit("system_stats", stats)
        await asyncio.sleep(2)