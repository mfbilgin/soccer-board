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

    except WebSocketDisconnect:
        print(f"[WS] Disconnected natively: {user.username}")
        await manager.disconnect(user_id)
    except Exception as e:
        print(f"[WS] SERVER CRASH ERROR in loop: {e}")
        import traceback
        traceback.print_exc()
        await manager.disconnect(user_id)
