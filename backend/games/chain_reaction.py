"""Chain Reaction: 2-6 oyunculu lobi; oyuncu-takım zinciri sırayla uzatılır,
süresinde cevap veremeyen elenir, son kalan havuzu alır."""
import asyncio
import random
import time

from games.base import GameMode
from games.lifecycle import (cancel_timer, db_session, log_match_event,
                             run_turn_timer, teardown_room)
from games.registry import register
from services.economy import award_winnings
from socket_manager import manager

TURN_SECONDS = 15
LOBBY_COUNTDOWN_SECONDS = 20
MAX_PLAYERS = 6
MIN_PLAYERS = 2


@register
class ChainReactionGame(GameMode):
    modes = ("chain_reaction",)

    def __init__(self):
        # tier -> bekleyen (waiting) lobinin room_id'si
        self.open_lobbies = {}

    # --- Lobi yönetimi ---

    async def join_lobby(self, user_id: str, username: str, rating: int, tier: int):
        room_id = self.open_lobbies.get(tier)
        room = manager.rooms.get(room_id) if room_id else None

        if not room or room.state != "waiting" or len(room.players) >= MAX_PLAYERS:
            room = manager.create_room("chain_reaction", tier)
            room_id = room.room_id
            self.open_lobbies[tier] = room_id

        manager.add_to_room(room, user_id, {"username": username, "rating": rating})

        await room.broadcast({
            "type": "lobby_update",
            "room_id": room_id,
            "players": room.player_data,
            "count": len(room.players)
        })

        if len(room.players) >= MAX_PLAYERS:
            lobby_task = room.game_state.get("lobby_timer_task")
            if lobby_task:
                lobby_task.cancel()
            if self.open_lobbies.get(tier) == room_id:
                del self.open_lobbies[tier]
            await self._begin(room_id)
        elif len(room.players) == MIN_PLAYERS:
            room.game_state["lobby_timer_task"] = asyncio.create_task(self._lobby_countdown(room_id, tier))

    async def _lobby_countdown(self, room_id: str, tier: int):
        try:
            await asyncio.sleep(LOBBY_COUNTDOWN_SECONDS)
        except asyncio.CancelledError:
            return

        room = manager.rooms.get(room_id)
        if not room or room.state != "waiting" or len(room.players) < MIN_PLAYERS:
            return

        if self.open_lobbies.get(tier) == room_id:
            del self.open_lobbies[tier]
        await self._begin(room_id)

    async def _begin(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room or room.state != "waiting":
            return
        room.state = "playing"
        await self.start(room_id)

    # --- Oyun akışı ---

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from chain_reaction import ChainReactionEngine
        with db_session() as db:
            engine = ChainReactionEngine(db)
            start = engine.pick_start_player()

        turn_order = list(room.players.keys())
        random.shuffle(turn_order)

        room.game_state = {
            "turn_order": turn_order,
            "active_idx": 0,
            "chain": [{"type": "player", "id": start["id"], "name": start["name"]}],
            "used_players": {start["id"]},
            "used_teams": set(),
            "eliminated": [],
            "turn_end_time": time.time() + TURN_SECONDS,
        }
        room.game_state["timer_task"] = asyncio.create_task(run_turn_timer(room_id, self._time_up))

        await room.broadcast({
            "type": "game_update",
            "action": "chain_ready",
            "start_entity": start,
            "turn_order": turn_order,
            "active_player": turn_order[0],
            "turn_end_time": room.game_state["turn_end_time"],
        })

    def actions(self):
        return {"chain_answer": self._answer}

    async def _time_up(self, room):
        gs = room.game_state
        active = gs["turn_order"][gs["active_idx"]]
        log_match_event(room.room_id, "SYSTEM", f"Chain: {active} suresi doldu, elendi.")
        await self._eliminate(room.room_id, active, reason="timeout")
        return False

    async def _answer(self, room, user_id, data, websocket):
        gs = room.game_state
        active = gs["turn_order"][gs["active_idx"]]
        if active != user_id:
            return

        entity_type = data.get("entity_type")
        if entity_type not in ("player", "team"):
            return
        try:
            entity_id = int(data.get("entity_id"))
        except (TypeError, ValueError):
            return

        last_node = gs["chain"][-1]
        expected_type = "team" if last_node["type"] == "player" else "player"
        if entity_type != expected_type:
            return

        from chain_reaction import ChainReactionEngine
        with db_session() as db:
            engine = ChainReactionEngine(db)
            valid = engine.validate_answer(last_node["type"], last_node["id"], entity_id, gs["used_players"], gs["used_teams"])

            if not valid:
                await websocket.send_json({"type": "chain_wrong_answer"})
                return

            name = engine.get_entity_name(entity_type, entity_id)
            if entity_type == "player":
                gs["used_players"].add(entity_id)
            else:
                gs["used_teams"].add(entity_id)
            gs["chain"].append({"type": entity_type, "id": entity_id, "name": name})
            log_match_event(room.room_id, user_id, f"Chain answer accepted: {name}")

            continuations = engine.get_valid_continuations(entity_type, entity_id, gs["used_players"], gs["used_teams"])
            if not continuations:
                new_start = engine.pick_start_player(exclude=gs["used_players"])
                gs["used_players"] = {new_start["id"]}
                gs["used_teams"] = set()
                gs["chain"] = [{"type": "player", "id": new_start["id"], "name": new_start["name"]}]
                log_match_event(room.room_id, "SYSTEM", "Zincir tikandi, yeni zincir basliyor.")
                await room.broadcast({
                    "type": "game_update",
                    "action": "chain_reset",
                    "message": "Zincir tıkandı, yeni zincir başlıyor!",
                    "start_entity": new_start,
                })
            else:
                await room.broadcast({
                    "type": "game_update",
                    "action": "chain_correct_answer",
                    "user_id": user_id,
                    "entity": {"type": entity_type, "id": entity_id, "name": name},
                })

        await self._advance_turn(room.room_id)

    async def _advance_turn(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        gs = room.game_state
        order = gs["turn_order"]
        n = len(order)
        idx = gs["active_idx"]
        for _ in range(n):
            idx = (idx + 1) % n
            if order[idx] not in gs["eliminated"]:
                break
        gs["active_idx"] = idx
        gs["turn_end_time"] = time.time() + TURN_SECONDS

        await room.broadcast({
            "type": "game_update",
            "action": "chain_turn_switch",
            "active_player": order[idx],
            "turn_end_time": gs["turn_end_time"],
        })

    async def _eliminate(self, room_id: str, user_id: str, reason: str):
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return

        gs = room.game_state
        if user_id not in gs["eliminated"]:
            gs["eliminated"].append(user_id)

        await room.broadcast({"type": "game_update", "action": "chain_player_eliminated", "user_id": user_id, "reason": reason})

        remaining = [u for u in gs["turn_order"] if u not in gs["eliminated"]]
        if len(remaining) <= 1:
            winner = remaining[0] if remaining else None
            await self._finish(room_id, winner)
            return

        await self._advance_turn(room_id)

    async def _finish(self, room_id: str, winner_id):
        room = manager.rooms.get(room_id)
        if not room:
            return
        room.state = "finished"
        cancel_timer(room)

        total_pool = room.entry_fee * len(room.player_data)
        if winner_id:
            log_match_event(room_id, "SYSTEM", f"Chain reaction bitti. Kazanan: {winner_id}")
            with db_session() as db:
                award_winnings(db, int(winner_id), total_pool)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "chain": room.game_state["chain"],
            "eliminated_order": room.game_state["eliminated"],
        })
        teardown_room(room_id)

    # --- Terk davranışları: N kişilik oyunda terk = eleme ---

    async def on_surrender(self, room, user_id: str):
        if room.state != "playing":
            return
        log_match_event(room.room_id, user_id, "Player SURRENDERED.")
        await self._eliminate(room.room_id, user_id, reason="surrender")

    async def on_abandon(self, room_id: str, user_id: str):
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return
        await self._eliminate(room_id, user_id, reason="disconnected")
