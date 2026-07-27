"""Find Player From Two: iki takımda da oynamış oyuncuyu ilk bulan turu alır;
3 tur kazanan maçı kazanır. Yanlış tahmin 3 saniyelik kilit getirir."""
import asyncio
import time

from games.base import GameMode
from games.lifecycle import (cancel_timer, db_session, log_match_event,
                             run_turn_timer, settle_two_player, teardown_room)
from games.registry import register
from socket_manager import manager

ROUND_SECONDS = 30
ROUNDS_TO_WIN = 3
WRONG_GUESS_LOCK_SECONDS = 3


@register
class FindTwoGame(GameMode):
    modes = ("find_two",)

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from find_two import FindTwoEngine
        with db_session() as db:
            engine = FindTwoEngine(db)
            round_data = engine.generate_round()

        room.game_state = {
            "round": round_data,
            "round_num": 1,
            "score": {pid: 0 for pid in room.players},
            "guess_locks": {},
            "turn_end_time": time.time() + ROUND_SECONDS,
        }
        room.game_state["timer_task"] = asyncio.create_task(run_turn_timer(room_id, self._time_up))
        await room.broadcast({
            "type": "game_update",
            "action": "find_two_round_ready",
            "round": round_data,
            "round_num": 1,
            "score": room.game_state["score"],
            "turn_end_time": room.game_state["turn_end_time"],
        })

    def actions(self):
        return {"find_two_guess": self._guess}

    async def _guess(self, room, user_id, data, websocket):
        gs = room.game_state
        now = time.time()
        if gs["guess_locks"].get(user_id, 0) > now:
            return

        try:
            entity_id = int(data.get("entity_id"))
        except (TypeError, ValueError):
            return

        from find_two import FindTwoEngine
        with db_session() as db:
            engine = FindTwoEngine(db)
            correct = engine.validate_guess(gs["round"], entity_id)

        if correct:
            log_match_event(room.room_id, user_id, f"Find Two: correct guess (player {entity_id}).")
            await self._next_round(room.room_id, round_winner=user_id)
        else:
            gs["guess_locks"][user_id] = now + WRONG_GUESS_LOCK_SECONDS
            await websocket.send_json({"type": "find_two_wrong"})

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Find Two: sure doldu, tur berabere.")
        await self._next_round(room.room_id, round_winner=None)
        return False

    async def _next_round(self, room_id: str, round_winner: str = None):
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return
        gs = room.game_state
        cancel_timer(room)

        if round_winner:
            gs["score"][round_winner] += 1

        await room.broadcast({
            "type": "game_update",
            "action": "find_two_round_result",
            "round_winner": round_winner,
            "round": gs["round"],
            "score": gs["score"],
        })

        if round_winner and gs["score"][round_winner] >= ROUNDS_TO_WIN:
            await self._finish(room_id, round_winner)
            return

        from find_two import FindTwoEngine
        with db_session() as db:
            engine = FindTwoEngine(db)
            round_data = engine.generate_round()

        gs["round"] = round_data
        gs["round_num"] += 1
        gs["guess_locks"] = {}
        gs["turn_end_time"] = time.time() + ROUND_SECONDS
        gs["timer_task"] = asyncio.create_task(run_turn_timer(room_id, self._time_up))
        await room.broadcast({
            "type": "game_update",
            "action": "find_two_round_ready",
            "round": round_data,
            "round_num": gs["round_num"],
            "score": gs["score"],
            "turn_end_time": gs["turn_end_time"],
        })

    async def _finish(self, room_id: str, winner_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        room.state = "finished"
        cancel_timer(room)

        log_match_event(room_id, "SYSTEM", f"Find Two bitti. Kazanan: {winner_id}")
        settle_two_player(room, winner_id)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "score": room.game_state["score"],
        })
        teardown_room(room_id)
