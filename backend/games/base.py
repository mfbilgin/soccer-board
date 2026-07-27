"""Tüm çok oyunculu oyun modlarının uyduğu sözleşme (Strategy deseni)."""
from abc import ABC, abstractmethod

from games.lifecycle import (FORFEIT_DISTANCE, cancel_timer, log_match_event,
                             settle_two_player, teardown_room)
from socket_manager import manager


class GameMode(ABC):
    """Bir oyun modunun yaşam döngüsü sözleşmesi.

    Her mod kendi başlatma (start), oyun içi aksiyonlarını (actions) ve
    oyunu terk etme davranışını (on_surrender / on_abandon) tanımlar.
    Varsayılan terk davranışları iki kişilik maçlara göredir; N kişilik
    modlar (ör. chain_reaction) bunları override eder.
    """

    modes: tuple = ()

    @abstractmethod
    async def start(self, room_id: str) -> None:
        """Oda 'playing' durumuna geçtiğinde ilk oyun durumunu kurar ve yayınlar."""

    def actions(self) -> dict:
        """WebSocket aksiyon adı -> async handler(room, user_id, data, websocket)."""
        return {}

    async def handle_action(self, room, user_id: str, action: str, data: dict, websocket):
        if action == "surrender":
            await self.on_surrender(room, user_id)
            return
        handler = self.actions().get(action)
        if handler:
            await handler(room, user_id, data, websocket)

    async def on_surrender(self, room, user_id: str):
        if room.state != "playing":
            return
        log_match_event(room.room_id, user_id, "Player SURRENDERED.")
        cancel_timer(room)
        room.state = "finished"

        p1, p2 = list(room.players.keys())
        winner_id = p2 if user_id == p1 else p1
        settle_two_player(room, winner_id)

        await room.broadcast({
            "type": "game_over",
            "winner_id": winner_id,
            "surrendered": user_id,
            "results": {
                p1: {"distance": 0 if winner_id == p1 else FORFEIT_DISTANCE, "total_sum": 0},
                p2: {"distance": 0 if winner_id == p2 else FORFEIT_DISTANCE, "total_sum": 0},
            }
        })
        teardown_room(room.room_id)

    async def on_abandon(self, room_id: str, user_id: str):
        """Oyuncu koptu ve süre tanındığı halde geri dönmedi: rakip hükmen kazanır."""
        room = manager.rooms.get(room_id)
        if not room or room.state != "playing":
            return
        room.state = "finished"
        cancel_timer(room)

        remaining = [pid for pid in room.player_data.keys() if pid != user_id]
        if remaining:
            winner_id = remaining[0]
            await room.broadcast({
                "type": "game_over",
                "reason": "opponent_disconnected",
                "winner_id": winner_id,
                "surrendered": user_id,
                "results": {
                    winner_id: {"distance": 0, "total_sum": 0, "message": "Rakip kaçtı"},
                    user_id: {"distance": FORFEIT_DISTANCE, "total_sum": 0, "message": "Bağlantı koptu"}
                }
            })
            log_match_event(room_id, user_id, "Player DISCONNECTED and did not return. Forfeit applied.")
            settle_two_player(room, winner_id)

        teardown_room(room_id)
