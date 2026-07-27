"""Flag Eleven: bayraklarla dizilmiş ilk 11'den takımı ilk bilen kazanır;
her oyuncunun 3 yanlış hakkı vardır."""
import asyncio
import time

from games.base import GameMode
from games.lifecycle import (cancel_timer, db_session, log_match_event,
                             run_turn_timer, settle_two_player, teardown_room)
from games.registry import register
from socket_manager import manager

GAME_SECONDS = 30
MAX_WRONG_GUESSES = 3


@register
class FlagElevenGame(GameMode):
    modes = ("flag_eleven",)

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from routers.flag_eleven import generate_puzzle
        with db_session() as db:
            puzzle = generate_puzzle(db)

        room.game_state = {
            "puzzle": puzzle,
            "wrong_counts": {pid: 0 for pid in room.players},
            "turn_end_time": time.time() + GAME_SECONDS,
        }
        room.game_state["timer_task"] = asyncio.create_task(run_turn_timer(room_id, self._time_up))
        await room.broadcast({
            "type": "game_update",
            "action": "flag_eleven_ready",
            "puzzle_id": puzzle["puzzle_id"],
            "positions": puzzle["positions"],
            "turn_end_time": room.game_state["turn_end_time"],
        })

    def actions(self):
        return {"flag_eleven_guess": self._guess}

    async def _guess(self, room, user_id, data, websocket):
        gs = room.game_state
        if gs["wrong_counts"].get(user_id, 0) >= MAX_WRONG_GUESSES:
            return

        from routers.flag_eleven import _is_match
        team_guess = data.get("team_guess", "")
        correct = _is_match(team_guess, gs["puzzle"]["team_name"])

        if correct:
            log_match_event(room.room_id, user_id, f"Flag Eleven: correct guess ({team_guess}).")
            await self._finish(room.room_id, winner_id=user_id)
            return

        gs["wrong_counts"][user_id] = gs["wrong_counts"].get(user_id, 0) + 1
        await websocket.send_json({"type": "flag_eleven_wrong", "wrong_count": gs["wrong_counts"][user_id]})

        if all(c >= MAX_WRONG_GUESSES for c in gs["wrong_counts"].values()):
            log_match_event(room.room_id, "SYSTEM", "Flag Eleven: iki taraf da hakkini tuketti, berabere.")
            await self._finish(room.room_id, winner_id=None)

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Flag Eleven: sure doldu, berabere.")
        await self._finish(room.room_id, winner_id=None)
        return True

    async def _finish(self, room_id: str, winner_id: str = None):
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return

        room.state = "finished"
        cancel_timer(room)

        team_name = room.game_state["puzzle"]["team_name"]
        if winner_id:
            log_match_event(room_id, "SYSTEM", f"Flag Eleven bitti. Kazanan: {winner_id}")
        settle_two_player(room, winner_id)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "team_name": team_name,
        })
        teardown_room(room_id)
