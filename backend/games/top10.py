"""Top 10 Guess: sırayla listedeki gizli oyuncular tahmin edilir, sıra puanı toplanır."""
import asyncio
import time

from games.base import GameMode
from games.lifecycle import (cancel_timer, db_session, log_match_event,
                             run_turn_timer, settle_two_player, shuffled_pair,
                             teardown_room)
from games.registry import register
from socket_manager import manager

TURN_SECONDS = 20
MAX_CONSECUTIVE_MISSES = 2


@register
class Top10Game(GameMode):
    modes = ("top10",)

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from routers.pyramid import generate_puzzle
        with db_session() as db:
            puzzle = generate_puzzle(db)

        first_player, _ = shuffled_pair(room)
        room.game_state = {
            "puzzle": puzzle,
            "revealed": [item["id"] for item in puzzle["items"] if not item["hidden"]],
            "active_player": first_player,
            "score": {pid: 0 for pid in room.players},
            "consecutive_misses": 0,
            "turn_end_time": time.time() + TURN_SECONDS,
        }
        room.game_state["timer_task"] = asyncio.create_task(run_turn_timer(room_id, self._time_up))
        await room.broadcast({
            "type": "game_update",
            "action": "top10_ready",
            "title": puzzle["title"],
            "subtitle": puzzle["subtitle"],
            "items": self._public_items(room.game_state),
            "active_player": first_player,
            "turn_end_time": room.game_state["turn_end_time"],
        })

    def actions(self):
        return {"top10_guess": self._guess}

    def _public_items(self, gs: dict) -> list:
        """Henüz bulunmamış oyuncuların adlarını gizleyerek listeyi döndürür."""
        revealed = set(gs["revealed"])
        return [item if item["id"] in revealed else {**item, "name": None} for item in gs["puzzle"]["items"]]

    async def _guess(self, room, user_id, data, websocket):
        gs = room.game_state
        if gs.get("active_player") != user_id:
            return

        try:
            guess_player_id = int(data.get("player_id"))
        except (TypeError, ValueError):
            return

        revealed = set(gs["revealed"])
        match = next((item for item in gs["puzzle"]["items"] if item["id"] == guess_player_id and item["id"] not in revealed), None)

        if match:
            gs["revealed"].append(match["id"])
            gs["score"][user_id] = gs["score"].get(user_id, 0) + match["rank"]
            log_match_event(room.room_id, user_id, f"Top10: correct guess rank {match['rank']}")

            await room.broadcast({
                "type": "game_update",
                "action": "top10_correct",
                "user_id": user_id,
                "item": match,
                "score": gs["score"],
            })

            if len(gs["revealed"]) >= len(gs["puzzle"]["items"]):
                await self._finish(room.room_id, reason="full")
                return

            await self._advance(room.room_id, user_id, was_correct=True)
        else:
            log_match_event(room.room_id, user_id, "Top10: wrong guess")
            await self._advance(room.room_id, user_id, was_correct=False)

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Top10: sure doldu.")
        await self._advance(room.room_id, room.game_state["active_player"], was_correct=False)
        return False

    async def _advance(self, room_id: str, user_id: str, was_correct: bool):
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return
        gs = room.game_state

        if was_correct:
            gs["consecutive_misses"] = 0
        else:
            gs["consecutive_misses"] += 1
            if gs["consecutive_misses"] >= MAX_CONSECUTIVE_MISSES:
                log_match_event(room_id, "SYSTEM", "Top10: deadlock, oyun erken bitiyor.")
                await self._finish(room_id, reason="deadlock")
                return

        p1, p2 = list(room.players.keys())
        gs["active_player"] = p2 if user_id == p1 else p1
        gs["turn_end_time"] = time.time() + TURN_SECONDS

        await room.broadcast({
            "type": "game_update",
            "action": "top10_turn_switch",
            "active_player": gs["active_player"],
            "turn_end_time": gs["turn_end_time"],
            "consecutive_misses": gs["consecutive_misses"],
        })

    async def _finish(self, room_id: str, reason: str):
        room = manager.rooms.get(room_id)
        if not room:
            return

        room.state = "finished"
        cancel_timer(room)

        gs = room.game_state
        p1, p2 = list(room.players.keys())
        s1 = gs["score"].get(p1, 0)
        s2 = gs["score"].get(p2, 0)

        winner_id = None
        if s1 > s2:
            winner_id = p1
        elif s2 > s1:
            winner_id = p2

        settle_two_player(room, winner_id)
        if winner_id:
            log_match_event(room_id, "SYSTEM", f"Top10 bitti ({reason}). Kazanan: {winner_id}")
        else:
            log_match_event(room_id, "SYSTEM", f"Top10 bitti ({reason}). Berabere.")

        await room.broadcast({
            "type": "game_over",
            "reason": reason,
            "winner_id": winner_id,
            "score": gs["score"],
            "items": gs["puzzle"]["items"],
        })
        teardown_room(room_id)
