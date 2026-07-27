"""Futbol XOX (tictactoe_1 / tictactoe_2): satır-sütun kriterlerine uyan
oyuncularla hücre kapma, 3'lü sıra veya çoğunluk kazanır."""
import asyncio
import time

from games.base import GameMode
from games.lifecycle import (cancel_timer, db_session, log_match_event,
                             run_turn_timer, settle_two_player, shuffled_pair,
                             teardown_room)
from games.registry import register
from socket_manager import manager

TURN_SECONDS = 30
MAX_CONSECUTIVE_PASSES = 2
BOARD_SIZE = 9


def _check_win(board: dict, symbol: str) -> bool:
    for r in range(3):
        if all(board.get(f"{r}-{c}", {}).get("symbol") == symbol for c in range(3)): return True
    for c in range(3):
        if all(board.get(f"{r}-{c}", {}).get("symbol") == symbol for r in range(3)): return True
    if all(board.get(f"{i}-{i}", {}).get("symbol") == symbol for i in range(3)): return True
    if all(board.get(f"{i}-{2-i}", {}).get("symbol") == symbol for i in range(3)): return True
    return False


@register
class TicTacToeGame(GameMode):
    modes = ("tictactoe_1", "tictactoe_2")

    async def start(self, room_id: str):
        room = manager.rooms.get(room_id)
        if not room:
            return
        from tictactoe import TicTacToeEngine
        with db_session() as db:
            engine = TicTacToeEngine(db)
            if room.game_mode == "tictactoe_1":
                grid = engine.generate_type1_grid()
            else:
                grid = engine.generate_type2_grid()

        p1, p2 = shuffled_pair(room)
        room.game_state = {
            "grid": grid,
            "board": {},
            "active_player": p1,
            "player_symbols": {p1: "X", p2: "O"},
            "consecutive_passes": 0,
            "turn_end_time": time.time() + TURN_SECONDS,
            "timer_task": asyncio.create_task(run_turn_timer(room_id, self._time_up))
        }

        await room.broadcast({
            "type": "game_update",
            "action": "tictactoe_ready",
            "grid": grid,
            "active_player": p1,
            "player_symbols": room.game_state["player_symbols"],
            "turn_end_time": room.game_state["turn_end_time"]
        })

    def actions(self):
        return {
            "tictactoe_guess": self._guess,
            "tictactoe_pass": self._manual_pass,
        }

    async def _time_up(self, room):
        log_match_event(room.room_id, "SYSTEM", "Turn time up! Automatic pass.")
        await self._pass_turn(room.room_id, room.game_state["active_player"], auto=True)
        return False

    async def _manual_pass(self, room, user_id, data, websocket):
        await self._pass_turn(room.room_id, user_id, auto=False)

    async def _guess(self, room, user_id, data, websocket):
        gs = room.game_state
        if gs.get("active_player") != user_id:
            return

        r_idx = int(data.get("rIdx"))
        c_idx = int(data.get("cIdx"))
        entity_id = int(data.get("entity_id"))
        cell_key = f"{r_idx}-{c_idx}"

        if cell_key in gs.get("board", {}):
            return  # Cell already taken

        grid = gs["grid"]
        row_id = grid["rows"][r_idx]["id"]
        col_id = grid["cols"][c_idx]["id"]

        with db_session() as db:
            from tictactoe import TicTacToeEngine
            engine = TicTacToeEngine(db)
            valid, _, _ = engine.validate_guess(row_id, col_id, entity_id, grid["type"])

        if not valid:
            log_match_event(room.room_id, user_id, f"Wrong guess at {r_idx},{c_idx}")
            await self._pass_turn(room.room_id, user_id, auto=False)
            return

        symbol = gs["player_symbols"][user_id]
        gs["board"][cell_key] = {"owner": user_id, "symbol": symbol}
        gs["consecutive_passes"] = 0
        log_match_event(room.room_id, user_id, f"Correct guess at {r_idx},{c_idx}")

        if _check_win(gs["board"], symbol):
            log_match_event(room.room_id, "SYSTEM", f"Player {user_id} won by 3 in a row.")
            await self._evaluate_winner(room.room_id, reason="win", explicit_winner=user_id)
            return

        if len(gs["board"]) == BOARD_SIZE:
            log_match_event(room.room_id, "SYSTEM", "Board full. Evaluating winner.")
            await self._evaluate_winner(room.room_id, reason="full")
            return

        await self._pass_turn(room.room_id, user_id, auto=False)

    async def _pass_turn(self, room_id: str, user_id: str, auto: bool = False):
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return

        if room.game_state.get("active_player") != user_id:
            return

        log_match_event(room_id, user_id, "Passed turn (auto=True)" if auto else "Passed turn manually")
        room.game_state["consecutive_passes"] += 1

        if room.game_state["consecutive_passes"] >= MAX_CONSECUTIVE_PASSES:
            log_match_event(room_id, "SYSTEM", "Deadlock reached. Evaluating winner.")
            await self._evaluate_winner(room_id, reason="deadlock")
            return

        p1, p2 = list(room.players.keys())
        next_player = p2 if user_id == p1 else p1

        room.game_state["active_player"] = next_player
        room.game_state["turn_end_time"] = time.time() + TURN_SECONDS

        await room.broadcast({
            "type": "game_update",
            "action": "tictactoe_turn_switch",
            "active_player": next_player,
            "turn_end_time": room.game_state["turn_end_time"],
            "consecutive_passes": room.game_state["consecutive_passes"],
            "board": room.game_state.get("board", {})
        })

    async def _evaluate_winner(self, room_id: str, reason: str, explicit_winner: str = None):
        room = manager.rooms.get(room_id)
        if not room:
            return

        room.state = "finished"
        cancel_timer(room)

        board = room.game_state.get("board", {})
        p1, p2 = list(room.players.keys())

        winner_id = explicit_winner
        if not winner_id:
            p1_count = sum(1 for c in board.values() if c["owner"] == p1)
            p2_count = sum(1 for c in board.values() if c["owner"] == p2)
            if p1_count > p2_count:
                winner_id = p1
            elif p2_count > p1_count:
                winner_id = p2

        settle_two_player(room, winner_id)

        with db_session() as db:
            from tictactoe import TicTacToeEngine
            engine = TicTacToeEngine(db)
            grid = room.game_state["grid"]
            row_ids = [r["id"] for r in grid["rows"]]
            col_ids = [c["id"] for c in grid["cols"]]
            answers = engine.get_answers(grid["type"], row_ids, col_ids)

        await room.broadcast({
            "type": "game_over",
            "reason": reason,
            "winner_id": winner_id,
            "board": board,
            "answers": answers,
            "results": {
                p1: {"message": f"{sum(1 for c in board.values() if c['owner'] == p1)} Hücre"},
                p2: {"message": f"{sum(1 for c in board.values() if c['owner'] == p2)} Hücre"}
            }
        })
        teardown_room(room_id)
