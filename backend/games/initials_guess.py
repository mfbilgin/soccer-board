"""Initials Guess: harf havuzlarından seçilen baş harflere uyan oyuncuyu
ilk bulan turu alır; 3 tur kazanan maçı kazanır."""
import asyncio
import time

from games.base import GameMode
from games.lifecycle import (cancel_timer, db_session, log_match_event,
                             run_turn_timer, settle_two_player, shuffled_pair,
                             teardown_room)
from games.registry import register
from socket_manager import manager

ROUND_SECONDS = 30
ROUNDS_TO_WIN = 3


@register
class InitialsGuessGame(GameMode):
    modes = ("initials_guess",)

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from initials_guess import InitialsGuessEngine
        with db_session() as db:
            engine = InitialsGuessEngine(db)
            pools = engine.generate_letter_pools()

        p1, p2 = shuffled_pair(room)
        room.game_state = {
            "start_picker": p1,
            "end_picker": p2,
            "pools": pools,
            "picks": {},
            "round_num": 1,
            "score": {pid: 0 for pid in room.players},
            "phase": "picking",
        }
        await room.broadcast({
            "type": "game_update",
            "action": "initials_pick_phase",
            "start_picker": p1,
            "end_picker": p2,
            "start_pool": pools["start_pool"],
            "end_pool": pools["end_pool"],
            "round_num": 1,
            "score": room.game_state["score"],
        })

    def actions(self):
        return {
            "initials_pick_letter": self._pick_letter,
            "initials_guess_answer": self._answer,
        }

    async def _pick_letter(self, room, user_id, data, websocket):
        gs = room.game_state
        if gs.get("phase") != "picking":
            return

        letter = (data.get("letter") or "").upper()
        if user_id == gs["start_picker"] and letter in gs["pools"]["start_pool"]:
            gs["picks"][user_id] = letter
        elif user_id == gs["end_picker"] and letter in gs["pools"]["end_pool"]:
            gs["picks"][user_id] = letter
        else:
            return

        await room.broadcast({"type": "game_update", "action": "initials_letter_locked", "user_id": user_id})

        if len(gs["picks"]) == 2:
            gs["phase"] = "guessing"
            gs["start_letter"] = gs["picks"][gs["start_picker"]]
            gs["end_letter"] = gs["picks"][gs["end_picker"]]
            gs["turn_end_time"] = time.time() + ROUND_SECONDS
            gs["timer_task"] = asyncio.create_task(run_turn_timer(room.room_id, self._time_up))
            await room.broadcast({
                "type": "game_update",
                "action": "initials_round_ready",
                "start_letter": gs["start_letter"],
                "end_letter": gs["end_letter"],
                "turn_end_time": gs["turn_end_time"],
            })

    async def _answer(self, room, user_id, data, websocket):
        gs = room.game_state
        if gs.get("phase") != "guessing":
            return

        try:
            entity_id = int(data.get("entity_id"))
        except (TypeError, ValueError):
            return

        from initials_guess import InitialsGuessEngine
        with db_session() as db:
            engine = InitialsGuessEngine(db)
            correct = engine.validate_guess(gs["start_letter"], gs["end_letter"], entity_id)

        if correct:
            log_match_event(room.room_id, user_id, f"Initials Guess: correct guess (player {entity_id}).")
            await self._next_round(room.room_id, round_winner=user_id)
        else:
            await websocket.send_json({"type": "initials_wrong"})

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Initials Guess: sure doldu, tur berabere.")
        await self._next_round(room.room_id, round_winner=None)
        return True

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
            "action": "initials_round_result",
            "round_winner": round_winner,
            "score": gs["score"],
        })

        if round_winner and gs["score"][round_winner] >= ROUNDS_TO_WIN:
            await self._finish(room_id, round_winner)
            return

        from initials_guess import InitialsGuessEngine
        with db_session() as db:
            engine = InitialsGuessEngine(db)
            pools = engine.generate_letter_pools()

        gs["pools"] = pools
        gs["picks"] = {}
        gs["phase"] = "picking"
        gs["round_num"] += 1
        await room.broadcast({
            "type": "game_update",
            "action": "initials_pick_phase",
            "start_picker": gs["start_picker"],
            "end_picker": gs["end_picker"],
            "start_pool": pools["start_pool"],
            "end_pool": pools["end_pool"],
            "round_num": gs["round_num"],
            "score": gs["score"],
        })

    async def _finish(self, room_id: str, winner_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        room.state = "finished"
        cancel_timer(room)

        log_match_event(room_id, "SYSTEM", f"Initials Guess bitti. Kazanan: {winner_id}")
        settle_two_player(room, winner_id)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "score": room.game_state["score"],
        })
        teardown_room(room_id)
