import uuid
import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional
from fastapi import WebSocket

from services.economy import refund_entry_fee_safe

ROOM_TIERS = [100, 250, 400, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000, 10000000]

DISCONNECT_GRACE_SECONDS = 15

class Room:
    def __init__(self, room_id: str, game_mode: str, entry_fee: int):
        self.room_id = room_id
        self.game_mode = game_mode
        self.entry_fee = entry_fee
        self.players: Dict[str, WebSocket] = {}
        self.player_data: Dict[str, dict] = {}
        self.state = "waiting" # waiting, playing, finished
        self.game_state: Dict[str, Any] = {}
        self.disconnect_tasks: Dict[str, asyncio.Task] = {}

    async def broadcast(self, message: dict):
        for ws in list(self.players.values()):
            try:
                await ws.send_json(message)
            except Exception:
                pass

    def public_state(self) -> dict:
        """Oyun durumunun JSON'a çevrilebilir kısmı (task/set gibi iç alanlar hariç)."""
        return {
            k: v for k, v in self.game_state.items()
            if isinstance(v, (str, int, float, bool, list, dict, type(None)))
        }

class ConnectionManager:
    """Bağlantı, oda ve eşleşme kuyruğu yönetimi.

    Oyun kurallarından habersizdir: oyun katmanı (games paketi) aşağıdaki
    kancaları enjekte eder, böylece bağımlılık yönü hep games -> socket_manager
    olur ve döngüsel import oluşmaz.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Room] = {}
        self.user_rooms: Dict[str, str] = {}
        # queues: (game_mode, entry_fee) -> [ {user_id, username, rating} ]
        self.queues: Dict[tuple, List[dict]] = {}
        # games paketi tarafından startup'ta enjekte edilen kancalar:
        self.on_match_start: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_player_abandon: Optional[Callable[[str, str], Awaitable[None]]] = None

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

        # Check if they were in a room (reconnect logic)
        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]
            room = self.rooms.get(room_id)
            if room:
                room.players[user_id] = websocket
                # Cancel disconnect task if exists
                if user_id in room.disconnect_tasks:
                    room.disconnect_tasks[user_id].cancel()
                    del room.disconnect_tasks[user_id]
                    asyncio.create_task(room.broadcast({"type": "player_reconnected", "user_id": user_id}))
                await websocket.send_json({"type": "reconnected", "room_id": room_id, "game_mode": room.game_mode, "state": room.public_state()})

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Remove from any queues
        for q_key, queue in self.queues.items():
            self.queues[q_key] = [p for p in queue if p['user_id'] != user_id]

        if user_id in self.user_rooms:
            room_id = self.user_rooms[user_id]
            room = self.rooms.get(room_id)
            if room and room.state == "playing":
                # Start a disconnect timer
                task = asyncio.create_task(self.handle_disconnect_timeout(user_id, room_id))
                room.disconnect_tasks[user_id] = task
                asyncio.create_task(room.broadcast({"type": "player_disconnected", "user_id": user_id}))
            elif room and room.state == "waiting":
                self.leave_room(user_id, room_id)

    async def handle_disconnect_timeout(self, user_id: str, room_id: str):
        try:
            await asyncio.sleep(DISCONNECT_GRACE_SECONDS)
        except asyncio.CancelledError:
            return # User reconnected

        room = self.rooms.get(room_id)
        # If this task wasn't cancelled, the user didn't reconnect.
        if room and room.state == "playing":
            room.disconnect_tasks.pop(user_id, None)
            if self.on_player_abandon:
                await self.on_player_abandon(room_id, user_id)

    def create_room(self, game_mode: str, entry_fee: int) -> Room:
        room_id = str(uuid.uuid4())
        room = Room(room_id, game_mode, entry_fee)
        self.rooms[room_id] = room
        return room

    def add_to_room(self, room: Room, user_id: str, player_info: dict):
        room.players[user_id] = self.active_connections[user_id]
        room.player_data[user_id] = player_info
        self.user_rooms[user_id] = room.room_id

    async def join_queue(self, user_id: str, username: str, rating: int, game_mode: str, entry_fee: int):
        q_key = (game_mode, entry_fee)
        if q_key not in self.queues:
            self.queues[q_key] = []

        # Check if they are already in queue
        if any(p['user_id'] == user_id for p in self.queues[q_key]):
            return

        # Are there opponents?
        if len(self.queues[q_key]) > 0:
            opponent = self.queues[q_key].pop(0)

            # If opponent disconnected while in queue, drop them and try next (or wait)
            if opponent['user_id'] not in self.active_connections:
                return await self.join_queue(user_id, username, rating, game_mode, entry_fee)

            room = self.create_room(game_mode, entry_fee)
            self.add_to_room(room, opponent['user_id'], {"username": opponent['username'], "rating": opponent['rating']})
            self.add_to_room(room, user_id, {"username": username, "rating": rating})
            room.state = "playing"

            await room.broadcast({
                "type": "match_found",
                "room_id": room.room_id,
                "game_mode": game_mode,
                "players": room.player_data
            })

            if self.on_match_start:
                await self.on_match_start(room.room_id)

        else:
            # Join queue
            self.queues[q_key].append({
                "user_id": user_id,
                "username": username,
                "rating": rating
            })

    def leave_room(self, user_id: str, room_id: str):
        if room_id in self.rooms:
            room = self.rooms[room_id]
            if user_id in room.player_data:
                if room.state == "waiting":
                    refund_entry_fee_safe(int(user_id), room.entry_fee)

                del room.player_data[user_id]
                if user_id in room.players:
                    del room.players[user_id]
                if user_id in self.user_rooms:
                    del self.user_rooms[user_id]

                if len(room.player_data) == 0:
                    if "lobby_timer_task" in room.game_state:
                        room.game_state["lobby_timer_task"].cancel()
                    del self.rooms[room_id]
                else:
                    asyncio.create_task(room.broadcast({
                        "type": "player_left",
                        "user_id": user_id,
                        "count": len(room.player_data)
                    }))

manager = ConnectionManager()
