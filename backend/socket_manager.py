import uuid
import asyncio
from typing import Dict, List, Any
from fastapi import WebSocket

ROOM_TIERS = [100, 250, 400, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000, 10000000]

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Room] = {}
        self.user_rooms: Dict[str, str] = {}
        # queues: (game_mode, entry_fee) -> [ {user_id, username, rating, websocket} ]
        self.queues: Dict[tuple, List[dict]] = {}
        # chain_lobby_rooms: entry_fee (tier) -> room_id of the currently-open (waiting) N-kişilik lobi
        self.chain_lobby_rooms: Dict[int, str] = {}

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
                await websocket.send_json({"type": "reconnected", "room_id": room_id, "game_mode": room.game_mode, "state": room.game_state})

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
            await asyncio.sleep(15) # 15 seconds grace period
        except asyncio.CancelledError:
            return # User reconnected

        room = self.rooms.get(room_id)
        # If this task wasn't cancelled, the user didn't reconnect.
        if room and room.state == "playing" and room.game_mode == "chain_reaction":
            if user_id in room.disconnect_tasks:
                del room.disconnect_tasks[user_id]
            from routers.multiplayer import chain_eliminate
            await chain_eliminate(room_id, user_id, reason="disconnected")
            return

        if room and room.state == "playing":
            room.state = "finished"
            winner_id = [pid for pid in room.player_data.keys() if pid != user_id]
            if winner_id:
                winner_id = winner_id[0]
                await room.broadcast({
                    "type": "game_over",
                    "reason": "opponent_disconnected",
                    "winner_id": winner_id,
                    "surrendered": user_id,
                    "results": {
                        winner_id: {"distance": 0, "total_sum": 0, "message": "Rakip kaçtı"},
                        user_id: {"distance": 999999, "total_sum": 0, "message": "Bağlantı koptu"}
                    }
                })
                # Process forfeit economy payout
                from routers.multiplayer import process_forfeit, log_match_event
                log_match_event(room_id, user_id, "Player DISCONNECTED and did not return. Forfeit applied.")
                process_forfeit(winner_id, user_id, room.entry_fee * 2)
            
            # Cleanup room
            for pid in list(room.player_data.keys()):
                if pid in self.user_rooms:
                    del self.user_rooms[pid]
            del self.rooms[room_id]

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
                
            # Create room
            room_id = str(uuid.uuid4())
            room = Room(room_id, game_mode, entry_fee)
            self.rooms[room_id] = room
            
            # Add players
            room.players[opponent['user_id']] = self.active_connections[opponent['user_id']]
            room.players[user_id] = self.active_connections[user_id]
            
            room.player_data[opponent['user_id']] = {"username": opponent['username'], "rating": opponent['rating']}
            room.player_data[user_id] = {"username": username, "rating": rating}
            
            self.user_rooms[opponent['user_id']] = room_id
            self.user_rooms[user_id] = room_id
            
            room.state = "playing"
            
            await room.broadcast({
                "type": "match_found",
                "room_id": room_id,
                "game_mode": game_mode,
                "players": room.player_data
            })
            
            # Start game specific logic
            from routers.multiplayer import initialize_game_state
            await initialize_game_state(room_id)
            
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
                    from routers.multiplayer import refund_fee_safe
                    refund_fee_safe(int(user_id), room.entry_fee)

                del room.player_data[user_id]
                if user_id in room.players:
                    del room.players[user_id]
                if user_id in self.user_rooms:
                    del self.user_rooms[user_id]

                if len(room.player_data) == 0:
                    if "lobby_timer_task" in room.game_state:
                        room.game_state["lobby_timer_task"].cancel()
                    for tier, rid in list(self.chain_lobby_rooms.items()):
                        if rid == room_id:
                            del self.chain_lobby_rooms[tier]
                    del self.rooms[room_id]
                else:
                    asyncio.create_task(room.broadcast({
                        "type": "player_left",
                        "user_id": user_id,
                        "count": len(room.player_data)
                    }))

    async def join_chain_lobby(self, user_id: str, username: str, rating: int, tier: int):
        room_id = self.chain_lobby_rooms.get(tier)
        room = self.rooms.get(room_id) if room_id else None

        if not room or room.state != "waiting" or len(room.players) >= 6:
            room_id = str(uuid.uuid4())
            room = Room(room_id, "chain_reaction", tier)
            self.rooms[room_id] = room
            self.chain_lobby_rooms[tier] = room_id

        room.players[user_id] = self.active_connections[user_id]
        room.player_data[user_id] = {"username": username, "rating": rating}
        self.user_rooms[user_id] = room_id

        await room.broadcast({
            "type": "lobby_update",
            "room_id": room_id,
            "players": room.player_data,
            "count": len(room.players)
        })

        from routers.multiplayer import start_chain_reaction_game, chain_lobby_countdown

        if len(room.players) >= 6:
            if "lobby_timer_task" in room.game_state:
                room.game_state["lobby_timer_task"].cancel()
            if self.chain_lobby_rooms.get(tier) == room_id:
                del self.chain_lobby_rooms[tier]
            await start_chain_reaction_game(room_id)
        elif len(room.players) == 2:
            room.game_state["lobby_timer_task"] = asyncio.create_task(chain_lobby_countdown(room_id, tier))

manager = ConnectionManager()
