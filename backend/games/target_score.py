"""Target Score (wire protocol id: "mode31"): iki oyuncu 90 saniyede hedef skora en yakın kadroyu kurar."""
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
class TargetScoreGame(GameMode):
    modes = ("mode31",)

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from routers.target_score import generate_puzzle
        with db_session() as db:
            puzzle = generate_puzzle(db)
        room.game_state = {
            "puzzle": puzzle,
            "submissions": {},
            "timer_task": asyncio.create_task(run_countdown(room_id, GAME_SECONDS, self._time_up))
        }
        await room.broadcast({"type": "game_update", "action": "puzzle_ready", "puzzle": puzzle})

    def actions(self):
        return {"submit_guess": self._submit_guess}

    async def _submit_guess(self, room, user_id, data, websocket):
        data["timestamp"] = time.time()
        room.game_state["submissions"][user_id] = data
        log_match_event(room.room_id, user_id, f"Locked in guess with {len(data.get('player_ids', []))} players.")
        if len(room.game_state["submissions"]) == 2:
            cancel_timer(room)
            await self._evaluate(room)
        else:
            await room.broadcast({"type": "player_ready", "user_id": user_id})

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Time is up! Evaluating game.")
        await self._evaluate(room)

    async def _evaluate(self, room):
        room.state = "finished"
        submissions = room.game_state.get("submissions", {})
        puzzle = room.game_state.get("puzzle")

        results = {}
        distances = {}
        with db_session() as db:
            from routers.target_score import compute_submission
            for uid in room.players.keys():
                sub = submissions.get(uid, {})
                p_ids = sub.get("player_ids", [])

                # Eksik kadro -> hükmen kayıp (sonsuz mesafe)
                if len(p_ids) < puzzle["player_count"]:
                    results[uid] = {"valid": False, "distance": FORFEIT_DISTANCE, "total_sum": 0, "message": "Incomplete submission"}
                    distances[uid] = FORFEIT_DISTANCE
                    log_match_event(room.room_id, uid, f"Disqualified: Incomplete submission ({len(p_ids)}/{puzzle['player_count']})")
                    continue

                res = compute_submission(db, puzzle["league"], puzzle["metric"], p_ids, puzzle["target"])
                results[uid] = res
                distances[uid] = res["distance"]
                log_match_event(room.room_id, uid, f"Valid submission: dist {res['distance']}, sum {res.get('total_sum', 0)}")

        winner_id = pick_closest_submitter(room, submissions, distances)
        log_match_event(room.room_id, "SYSTEM", f"Evaluation complete. Winner: {winner_id}")
        settle_two_player(room, winner_id)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "results": results
        })
        teardown_room(room.room_id)
