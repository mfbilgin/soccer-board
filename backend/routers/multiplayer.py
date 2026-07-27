"""Çok oyunculu WebSocket girişi.

Sorumluluğu üç şeyle sınırlıdır: kimlik doğrulama, kuyruk/lobi aksiyonları
ve oyun içi aksiyonların odanın oyun moduna (games paketi) yönlendirilmesi.
Oyun kuralları burada yaşamaz; yeni oyun modu eklemek için bu dosyaya
dokunmak gerekmez.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError

import models
import security
from database import SessionLocal
from games import get_game
from services.economy import deduct_entry_fee_safe, refund_entry_fee_safe
from socket_manager import manager

router = APIRouter(prefix="/api/multiplayer", tags=["Multiplayer"])
ws_router = APIRouter()


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


async def _charge_entry_fee(websocket: WebSocket, token: str, tier: int):
    """Güncel kullanıcıyı çekip giriş ücretini keser; başarısızsa hata yollar."""
    user = await get_current_user_ws(token)
    if not user or user.chips < tier:
        await websocket.send_json({"type": "error", "message": "Yeterli Chip yok"})
        return None
    if not deduct_entry_fee_safe(user.id, tier):
        await websocket.send_json({"type": "error", "message": "Bakiyeniz kesilemedi"})
        return None
    return user


async def _handle_join_queue(websocket, user_id, token, data):
    tier = int(data.get("tier"))
    game_mode = data.get("game_mode", "mode31")

    user = await _charge_entry_fee(websocket, token, tier)
    if user:
        await websocket.send_json({"type": "queue_joined", "tier": tier})
        await manager.join_queue(user_id, user.username, user.rating, game_mode, tier)


async def _handle_leave_queue(websocket, user_id, token, data):
    tier = int(data.get("tier"))
    game_mode = data.get("game_mode", "mode31")
    q_key = (game_mode, tier)

    queue = manager.queues.get(q_key, [])
    if not any(p['user_id'] == user_id for p in queue):
        return

    manager.queues[q_key] = [p for p in queue if p['user_id'] != user_id]
    refund_entry_fee_safe(int(user_id), tier)
    await websocket.send_json({"type": "queue_left"})


async def _handle_join_chain_lobby(websocket, user_id, token, data):
    tier = int(data.get("tier"))

    user = await _charge_entry_fee(websocket, token, tier)
    if user:
        await get_game("chain_reaction").join_lobby(user_id, user.username, user.rating, tier)


async def _handle_leave_chain_lobby(websocket, user_id, token, data):
    room_id = manager.user_rooms.get(user_id)
    room = manager.rooms.get(room_id) if room_id else None
    if room and room.state == "waiting":
        manager.leave_room(user_id, room_id)
        await websocket.send_json({"type": "lobby_left"})


# Odaya girmeden önce anlamlı olan aksiyonlar; gerisi oyun moduna gider.
LOBBY_HANDLERS = {
    "join_queue": _handle_join_queue,
    "leave_queue": _handle_leave_queue,
    "join_chain_lobby": _handle_join_chain_lobby,
    "leave_chain_lobby": _handle_leave_chain_lobby,
}


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

            lobby_handler = LOBBY_HANDLERS.get(action)
            if lobby_handler:
                await lobby_handler(websocket, user_id, token, data)
                continue

            room_id = manager.user_rooms.get(user_id)
            room = manager.rooms.get(room_id) if room_id else None
            if not room or room.state != "playing":
                continue

            game = get_game(room.game_mode)
            if game:
                await game.handle_action(room, user_id, action, data, websocket)

    except WebSocketDisconnect:
        print(f"[WS] Disconnected natively: {user.username}")
        await manager.disconnect(user_id)
    except Exception as e:
        print(f"[WS] SERVER CRASH ERROR in loop: {e}")
        import traceback
        traceback.print_exc()
        await manager.disconnect(user_id)
