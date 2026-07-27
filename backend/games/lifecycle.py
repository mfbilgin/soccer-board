"""Oyun modlarının paylaştığı yaşam döngüsü yardımcıları:
maç loglama, zamanlayıcılar, maç sonu ödemesi ve oda temizliği.
"""
import asyncio
import json
import os
import random
import time
from contextlib import contextmanager

import models
from database import SessionLocal
from services.economy import award_winnings, update_rating
from socket_manager import manager

FORFEIT_DISTANCE = 999999


@contextmanager
def db_session():
    """Kapanışı garanti edilen kısa ömürlü DB oturumu."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def cancel_timer(room):
    task = room.game_state.get("timer_task")
    if task:
        task.cancel()


def teardown_room(room_id: str):
    """Odayı ve oyuncu -> oda eşlemelerini kaldırır."""
    room = manager.rooms.get(room_id)
    if not room:
        return
    for pid in list(room.player_data.keys()):
        manager.user_rooms.pop(pid, None)
    manager.rooms.pop(room_id, None)


def settle_two_player(room, winner_id):
    """İki kişilik maç sonucunu işler: kazanan varsa ödül + rating,
    beraberlikte iki tarafa da giriş ücreti iadesi."""
    with db_session() as db:
        players = list(room.player_data.keys())
        if winner_id:
            loser_id = next(pid for pid in players if pid != winner_id)
            award_winnings(db, int(winner_id), room.entry_fee * 2)
            update_rating(db, int(winner_id), int(loser_id))
        else:
            for pid in players:
                user = db.query(models.User).filter(models.User.id == int(pid)).first()
                if user:
                    user.chips += room.entry_fee
            db.commit()


def shuffled_pair(room):
    """İki oyuncuyu rastgele sırayla döndürür (kim başlayacak kurası)."""
    p1, p2 = list(room.players.keys())
    if random.random() > 0.5:
        p1, p2 = p2, p1
    return p1, p2


def pick_closest_submitter(room, submissions: dict, distances: dict):
    """Hedefe en yakın gönderimi yapan oyuncuyu seçer.

    Eşitlikte, hükmen kaybetmemişlerse ilk gönderen kazanır; aksi halde berabere.
    """
    p1, p2 = list(room.players.keys())
    d1 = distances.get(p1, FORFEIT_DISTANCE)
    d2 = distances.get(p2, FORFEIT_DISTANCE)

    if d1 < d2:
        return p1
    if d2 < d1:
        return p2
    if d1 == FORFEIT_DISTANCE:
        return None

    t1 = submissions.get(p1, {}).get("timestamp", float("inf"))
    t2 = submissions.get(p2, {}).get("timestamp", float("inf"))
    if t1 < t2:
        return p1
    if t2 < t1:
        return p2
    return None


async def run_turn_timer(room_id: str, on_timeout):
    """game_state['turn_end_time'] dolduğunda on_timeout(room) çağıran döngü.

    Bir oyuncu kopukken sayaç duraklar. on_timeout True dönerse döngü sonlanır.
    """
    try:
        while True:
            room = manager.rooms.get(room_id)
            if not room or room.state != "playing":
                return

            if room.disconnect_tasks:
                await asyncio.sleep(1)
                continue

            if time.time() >= room.game_state.get("turn_end_time", 0):
                if await on_timeout(room):
                    return

            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass


async def run_countdown(room_id: str, seconds: int, on_expire):
    """Toplam maç süresi sayacı; kopukluklarda duraklar, süre bitince on_expire(room)."""
    try:
        elapsed = 0
        while elapsed < seconds:
            room = manager.rooms.get(room_id)
            if not room or room.state != "playing":
                return

            if room.disconnect_tasks:
                await asyncio.sleep(1)
                continue

            elapsed += 1
            await asyncio.sleep(1)

        room = manager.rooms.get(room_id)
        if room and room.state == "playing":
            await on_expire(room)
    except asyncio.CancelledError:
        pass
