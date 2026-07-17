from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
import models, security
from database import SessionLocal
from socket_manager import manager
import asyncio
from services.economy import deduct_entry_fee, award_winnings, update_rating
import os
import json
import time

router = APIRouter(prefix="/api/multiplayer", tags=["Multiplayer"])
ws_router = APIRouter()

def log_match_event(room_id: str, user_id: str, event_desc: str):
    log_dir = "match_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"{room_id}.jsonl")
    log_entry = {
        "timestamp": time.time(),
        "user": user_id,
        "event": event_desc
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

async def get_current_user_ws(token: str):
    db = SessionLocal()
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return None
        user = db.query(models.User).filter(models.User.username == username).first()
        return user
    except JWTError:
        return None
    finally:
        db.close()

def deduct_fee_safe(user_id: int, fee: int) -> bool:
    db = SessionLocal()
    try:
        return deduct_entry_fee(db, user_id, fee)
    finally:
        db.close()

def process_forfeit(winner_id: str, loser_id: str, total_pool: int):
    db = SessionLocal()
    try:
        award_winnings(db, int(winner_id), total_pool)
        update_rating(db, int(winner_id), int(loser_id))
    finally:
        db.close()

async def initialize_game_state(room_id: str):
    room = manager.rooms.get(room_id)
    if not room: return
    
    if room.game_mode == "mode31":
        db = SessionLocal()
        try:
            from routers.mode_3_1 import generate_puzzle
            puzzle = generate_puzzle(db)
            room.game_state = {
                "puzzle": puzzle,
                "submissions": {},
                "timer_task": asyncio.create_task(mode31_timer(room_id))
            }
            await room.broadcast({"type": "game_update", "action": "puzzle_ready", "puzzle": puzzle})
        finally:
            db.close()
            
    elif room.game_mode in ["tictactoe_1", "tictactoe_2"]:
        db = SessionLocal()
        try:
            from tictactoe import TicTacToeEngine
            import random
            engine = TicTacToeEngine(db)
            grid_type = 1 if room.game_mode == "tictactoe_1" else 2
            
            if grid_type == 1:
                grid = engine.generate_type1_grid()
            else:
                grid = engine.generate_type2_grid()
                
            p1, p2 = list(room.players.keys())
            if random.random() > 0.5:
                p1, p2 = p2, p1
                
            room.game_state = {
                "grid": grid,
                "board": {},
                "active_player": p1,
                "player_symbols": {p1: "X", p2: "O"},
                "consecutive_passes": 0,
                "turn_end_time": time.time() + 30,
                "timer_task": asyncio.create_task(tictactoe_timer(room_id))
            }
            
            await room.broadcast({
                "type": "game_update",
                "action": "tictactoe_ready",
                "grid": grid,
                "active_player": p1,
                "player_symbols": room.game_state["player_symbols"],
                "turn_end_time": room.game_state["turn_end_time"]
            })
        finally:
            db.close()

async def tictactoe_timer(room_id: str):
    try:
        while True:
            room = manager.rooms.get(room_id)
            if not room or room.state != "playing":
                return
            
            if len(room.disconnect_tasks) > 0:
                await asyncio.sleep(1)
                continue
                
            turn_end = room.game_state.get("turn_end_time", 0)
            if time.time() >= turn_end:
                log_match_event(room_id, "SYSTEM", "Turn time up! Automatic pass.")
                await tictactoe_pass(room_id, room.game_state["active_player"], auto=True)
                
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

async def tictactoe_pass(room_id: str, user_id: str, auto=False):
    room = manager.rooms.get(room_id)
    if not room or room.state != "playing": return
    
    if room.game_state.get("active_player") != user_id:
        return
        
    log_match_event(room_id, user_id, "Passed turn (auto=True)" if auto else "Passed turn manually")
    room.game_state["consecutive_passes"] += 1
    
    if room.game_state["consecutive_passes"] >= 2:
        log_match_event(room_id, "SYSTEM", "Deadlock reached. Evaluating winner.")
        await evaluate_tictactoe_winner(room_id, reason="deadlock")
        return
        
    p1, p2 = list(room.players.keys())
    next_player = p2 if user_id == p1 else p1
    
    room.game_state["active_player"] = next_player
    room.game_state["turn_end_time"] = time.time() + 30
    
    await room.broadcast({
        "type": "game_update",
        "action": "tictactoe_turn_switch",
        "active_player": next_player,
        "turn_end_time": room.game_state["turn_end_time"],
        "consecutive_passes": room.game_state["consecutive_passes"],
        "board": room.game_state.get("board", {})
    })

def check_tictactoe_win(board: dict, symbol: str) -> bool:
    for r in range(3):
        if all(board.get(f"{r}-{c}", {}).get("symbol") == symbol for c in range(3)): return True
    for c in range(3):
        if all(board.get(f"{r}-{c}", {}).get("symbol") == symbol for r in range(3)): return True
    if all(board.get(f"{i}-{i}", {}).get("symbol") == symbol for i in range(3)): return True
    if all(board.get(f"{i}-{2-i}", {}).get("symbol") == symbol for i in range(3)): return True
    return False

async def evaluate_tictactoe_winner(room_id: str, reason: str, explicit_winner: str = None):
    room = manager.rooms.get(room_id)
    if not room: return
    
    room.state = "finished"
    if "timer_task" in room.game_state:
        room.game_state["timer_task"].cancel()
        
    board = room.game_state.get("board", {})
    p1, p2 = list(room.players.keys())
    
    winner_id = explicit_winner
    if not winner_id:
        p1_count = sum(1 for c in board.values() if c["owner"] == p1)
        p2_count = sum(1 for c in board.values() if c["owner"] == p2)
        if p1_count > p2_count: winner_id = p1
        elif p2_count > p1_count: winner_id = p2
        else: winner_id = None
            
    db = SessionLocal()
    try:
        if winner_id:
            loser_id = p2 if winner_id == p1 else p1
            award_winnings(db, int(winner_id), room.entry_fee * 2)
            update_rating(db, int(winner_id), int(loser_id))
        else:
            user1 = db.query(models.User).filter(models.User.id == int(p1)).first()
            user2 = db.query(models.User).filter(models.User.id == int(p2)).first()
            if user1: user1.chips += room.entry_fee
            if user2: user2.chips += room.entry_fee
            db.commit()
            
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
    finally:
        db.close()
        for pid in list(room.players.keys()):
            if pid in manager.user_rooms:
                del manager.user_rooms[pid]
        if room_id in manager.rooms:
            del manager.rooms[room_id]

async def mode31_timer(room_id: str):
    try:
        elapsed = 0
        while elapsed < 90:
            room = manager.rooms.get(room_id)
            if not room or room.state != "playing":
                return
            
            # If someone is disconnected, pause the timer
            if len(room.disconnect_tasks) > 0:
                await asyncio.sleep(1)
                continue
                
            elapsed += 1
            await asyncio.sleep(1)
            
        # 90 seconds elapsed (excluding pauses)
        room = manager.rooms.get(room_id)
        if room and room.state == "playing":
            log_match_event(room_id, "SYSTEM", "Time is up! Evaluating game.")
            await evaluate_mode31(room_id)
    except asyncio.CancelledError:
        pass # Task cancelled because both submitted

async def evaluate_mode31(room_id: str):
    room = manager.rooms.get(room_id)
    if not room: return
    
    room.state = "finished"
    submissions = room.game_state.get("submissions", {})
    puzzle = room.game_state.get("puzzle")
    
    db = SessionLocal()
    try:
        from routers.mode_3_1 import validate_submission
        results = {}
        distances = {}
        for uid in room.players.keys():
            sub = submissions.get(uid, {})
            p_ids = sub.get("player_ids", [])
            
            # Anti-Cheat / Disqualification Check
            if len(p_ids) < puzzle["player_count"]:
                # Incomplete board -> automatic forfeit (infinite distance)
                results[uid] = {"valid": False, "distance": 999999, "total_sum": 0, "message": "Incomplete submission"}
                distances[uid] = 999999
                log_match_event(room_id, uid, f"Disqualified: Incomplete submission ({len(p_ids)}/{puzzle['player_count']})")
                continue
                
            payload = {
                "league": puzzle["league"],
                "metric": puzzle["metric"],
                "target": puzzle["target"],
                "player_ids": p_ids
            }
            res = validate_submission(payload, db)
            results[uid] = res
            distances[uid] = res["distance"]
            log_match_event(room_id, uid, f"Valid submission: dist {res['distance']}, sum {res.get('total_sum', 0)}")
            
        p1, p2 = list(room.players.keys())
        d1 = distances.get(p1, 999999)
        d2 = distances.get(p2, 999999)
        
        t1 = submissions.get(p1, {}).get("timestamp", float('inf'))
        t2 = submissions.get(p2, {}).get("timestamp", float('inf'))
        
        winner_id = None
        if d1 < d2:
            winner_id = p1
        elif d2 < d1:
            winner_id = p2
        else:
            # Eşitlik durumunda (Tie-Breaker), ilk gönderen kazanır
            if d1 != 999999: # Only tie-break if they actually didn't forfeit
                if t1 < t2:
                    winner_id = p1
                elif t2 < t1:
                    winner_id = p2
            
        log_match_event(room_id, "SYSTEM", f"Evaluation complete. Winner: {winner_id}")
            
        if winner_id:
            loser_id = p2 if winner_id == p1 else p1
            award_winnings(db, int(winner_id), room.entry_fee * 2)
            update_rating(db, int(winner_id), int(loser_id))
        else:
            # Draw - refund
            user1 = db.query(models.User).filter(models.User.id == int(p1)).first()
            user2 = db.query(models.User).filter(models.User.id == int(p2)).first()
            if user1: user1.chips += room.entry_fee
            if user2: user2.chips += room.entry_fee
            db.commit()
            
        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "results": results
        })
    finally:
        db.close()
        for pid in list(room.players.keys()):
            if pid in manager.user_rooms:
                del manager.user_rooms[pid]
        if room_id in manager.rooms:
            del manager.rooms[room_id]

@ws_router.websocket("/api/multiplayer/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    print(f"[WS] Connection attempt... token: {token[:15]}...")
    user = await get_current_user_ws(token)
    if not user:
        print("[WS] Connection REJECTED (code 1008): Invalid token or user not found.")
        await websocket.close(code=1008)
        return
        
    user_id = str(user.id)
    await manager.connect(websocket, user_id)
    print(f"[WS] Connection ACCEPTED for user: {user.username} (ID: {user_id})")
    
    try:
        while True:
            data = await websocket.receive_json()
            print(f"[WS] Msg from {user.username}: {data}")
            action = data.get("action")
            
            if action == "join_queue":
                tier = int(data.get("tier"))
                game_mode = data.get("game_mode", "mode31")
                
                user_fresh = await get_current_user_ws(token)
                if user_fresh and user_fresh.chips >= tier:
                    if deduct_fee_safe(user_fresh.id, tier):
                        await websocket.send_json({"type": "queue_joined", "tier": tier})
                        await manager.join_queue(user_id, user_fresh.username, user_fresh.rating, game_mode, tier)
                    else:
                        await websocket.send_json({"type": "error", "message": "Bakiyeniz kesilemedi"})
                else:
                    await websocket.send_json({"type": "error", "message": "Yeterli Chip yok"})
                    
            elif action == "leave_queue":
                tier = int(data.get("tier"))
                game_mode = data.get("game_mode", "mode31")
                q_key = (game_mode, tier)
                
                # Check if user is actually in queue
                if q_key in manager.queues and any(p['user_id'] == user_id for p in manager.queues[q_key]):
                    # Remove from queue
                    manager.queues[q_key] = [p for p in manager.queues[q_key] if p['user_id'] != user_id]
                    # Refund fee
                    db = SessionLocal()
                    try:
                        u = db.query(models.User).filter(models.User.id == int(user_id)).first()
                        u.chips += tier
                        db.commit()
                    finally:
                        db.close()
                    await websocket.send_json({"type": "queue_left"})
                
            elif action == "submit_guess":
                import time
                room_id = manager.user_rooms.get(user_id)
                if room_id and room_id in manager.rooms:
                    room = manager.rooms[room_id]
                    if room.game_mode == "mode31" and room.state == "playing":
                        data["timestamp"] = time.time()
                        room.game_state["submissions"][user_id] = data
                        log_match_event(room_id, user_id, f"Locked in guess with {len(data.get('player_ids', []))} players.")
                        if len(room.game_state["submissions"]) == 2:
                            room.game_state["timer_task"].cancel()
                            await evaluate_mode31(room_id)
                        else:
                            await room.broadcast({"type": "player_ready", "user_id": user_id})

            elif action == "surrender":
                room_id = manager.user_rooms.get(user_id)
                if room_id and room_id in manager.rooms:
                    room = manager.rooms[room_id]
                    if room.state == "playing":
                        log_match_event(room_id, user_id, "Player SURRENDERED.")
                        if "timer_task" in room.game_state:
                            room.game_state["timer_task"].cancel()
                        room.state = "finished"
                        p1, p2 = list(room.players.keys())
                        winner_id = p2 if user_id == p1 else p1
                        
                        db = SessionLocal()
                        try:
                            award_winnings(db, int(winner_id), room.entry_fee * 2)
                            update_rating(db, int(winner_id), int(user_id))
                        finally:
                            db.close()
                            
                        await room.broadcast({
                            "type": "game_over",
                            "winner_id": winner_id,
                            "surrendered": user_id,
                            "results": {
                                p1: {"distance": 0 if winner_id == p1 else 999999, "total_sum": 0},
                                p2: {"distance": 0 if winner_id == p2 else 999999, "total_sum": 0}
                            }
                        })
                        for pid in list(room.players.keys()):
                            if pid in manager.user_rooms:
                                del manager.user_rooms[pid]
                        if room_id in manager.rooms:
                            del manager.rooms[room_id]

            elif action == "tictactoe_guess":
                room_id = manager.user_rooms.get(user_id)
                if room_id and room_id in manager.rooms:
                    room = manager.rooms[room_id]
                    if room.state == "playing" and room.game_mode.startswith("tictactoe"):
                        if room.game_state.get("active_player") != user_id:
                            continue # Ignore if not their turn
                            
                        r_idx = int(data.get("rIdx"))
                        c_idx = int(data.get("cIdx"))
                        entity_id = int(data.get("entity_id"))
                        cell_key = f"{r_idx}-{c_idx}"
                        
                        if cell_key in room.game_state.get("board", {}):
                            continue # Cell already taken
                            
                        grid = room.game_state["grid"]
                        row_id = grid["rows"][r_idx]["id"]
                        col_id = grid["cols"][c_idx]["id"]
                        
                        db = SessionLocal()
                        valid = False
                        try:
                            from tictactoe import TicTacToeEngine
                            engine = TicTacToeEngine(db)
                            valid = engine.validate_answer(grid["type"], row_id, col_id, entity_id)
                        finally:
                            db.close()
                            
                        if valid:
                            symbol = room.game_state["player_symbols"][user_id]
                            room.game_state["board"][cell_key] = {"owner": user_id, "symbol": symbol}
                            room.game_state["consecutive_passes"] = 0
                            
                            log_match_event(room_id, user_id, f"Correct guess at {r_idx},{c_idx}")
                            
                            # Check win
                            if check_tictactoe_win(room.game_state["board"], symbol):
                                log_match_event(room_id, "SYSTEM", f"Player {user_id} won by 3 in a row.")
                                await evaluate_tictactoe_winner(room_id, reason="win", explicit_winner=user_id)
                                continue
                                
                            # Check full board draw
                            if len(room.game_state["board"]) == 9:
                                log_match_event(room_id, "SYSTEM", "Board full. Evaluating winner.")
                                await evaluate_tictactoe_winner(room_id, reason="full")
                                continue
                                
                            # Next turn
                            await tictactoe_pass(room_id, user_id, auto=False)
                        else:
                            # Wrong guess - pass turn
                            log_match_event(room_id, user_id, f"Wrong guess at {r_idx},{c_idx}")
                            await tictactoe_pass(room_id, user_id, auto=False)
                            
            elif action == "tictactoe_pass":
                room_id = manager.user_rooms.get(user_id)
                if room_id and room_id in manager.rooms:
                    room = manager.rooms[room_id]
                    if room.state == "playing" and room.game_mode.startswith("tictactoe"):
                        await tictactoe_pass(room_id, user_id, auto=False)

    except WebSocketDisconnect:
        print(f"[WS] Disconnected natively: {user.username}")
        await manager.disconnect(user_id)
    except Exception as e:
        print(f"[WS] SERVER CRASH ERROR in loop: {e}")
        import traceback
        traceback.print_exc()
        await manager.disconnect(user_id)
