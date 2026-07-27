"""Extreme Squad: iki oyuncu 90 saniyede kritere en uygun kadroyu kurar."""
import asyncio
import time

from games.base import GameMode
from games.lifecycle import (FORFEIT_DISTANCE, cancel_timer, db_session,
                             log_match_event, pick_closest_submitter,
                             run_countdown, settle_two_player, teardown_room)
from games.registry import register
from socket_manager import manager

GAME_SECONDS = 90


@register
class ExtremeSquadGame(GameMode):
    modes = ("extreme_squad",)

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from routers.extreme_squad import generate_puzzle
        with db_session() as db:
            puzzle = generate_puzzle(db)
        room.game_state = {
            "puzzle": puzzle,
            "submissions": {},
            "locked_slots": {pid: [] for pid in room.players},
            "timer_task": asyncio.create_task(run_countdown(room_id, GAME_SECONDS, self._time_up))
        }
        await room.broadcast({"type": "game_update", "action": "extreme_ready", "puzzle": puzzle})

    def actions(self):
        return {
            "extreme_lock_slot": self._lock_slot,
            "extreme_submit": self._submit,
        }

    async def _lock_slot(self, room, user_id, data, websocket):
        slot_id = data.get("slot_id")
        locked = room.game_state.setdefault("locked_slots", {}).setdefault(user_id, [])
        if slot_id not in locked:
            locked.append(slot_id)
        await room.broadcast({"type": "game_update", "action": "extreme_slot_locked", "user_id": user_id, "slot_id": slot_id})

    async def _submit(self, room, user_id, data, websocket):
        data["timestamp"] = time.time()
        room.game_state["submissions"][user_id] = data
        log_match_event(room.room_id, user_id, f"Extreme Squad locked in with {len(data.get('player_ids', []))} players.")
        if len(room.game_state["submissions"]) == 2:
            cancel_timer(room)
            await self._evaluate(room)
        else:
            await room.broadcast({"type": "player_ready", "user_id": user_id})

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Extreme Squad: sure doldu.")
        await self._evaluate(room)

    async def _evaluate(self, room):
        room.state = "finished"
        cancel_timer(room)
        submissions = room.game_state.get("submissions", {})
        puzzle = room.game_state.get("puzzle")

        results = {}
        distances = {}
        with db_session() as db:
            from routers.extreme_squad import compute_extreme_submission
            for uid in room.players.keys():
                sub = submissions.get(uid, {})
                player_ids = sub.get("player_ids", [])
                res = compute_extreme_submission(db, puzzle["criterion"], puzzle["slots"], player_ids)
                results[uid] = res
                distances[uid] = res["distance"] if res["valid"] else FORFEIT_DISTANCE
                log_match_event(room.room_id, uid, f"Extreme Squad submission: valid={res['valid']} distance={res.get('distance')}")

        winner_id = pick_closest_submitter(room, submissions, distances)
        log_match_event(room.room_id, "SYSTEM", f"Extreme Squad evaluation complete. Winner: {winner_id}")
        settle_two_player(room, winner_id)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "results": results
        })
        teardown_room(room.room_id)
