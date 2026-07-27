"""Çok oyunculu oyun modları paketi.

Her modül kendi GameMode alt sınıfını @register ile registry'ye kaydeder.
Yeni bir oyun modu eklemek için: games/ altında yeni bir modül yaz,
@register ile işaretle ve aşağıdaki import listesine ekle — router'a veya
socket_manager'a dokunmak gerekmez.
"""
from games.registry import get_game
from socket_manager import manager

# Import etmek kayıt için yeterlidir (her modülde @register çalışır).
from games import (chain_reaction, extreme_squad, find_two, flag_eleven,
                   initials_guess, target_score, tictactoe, top10)

__all__ = ["get_game"]


async def _start_game(room_id: str):
    room = manager.rooms.get(room_id)
    if not room:
        return
    game = get_game(room.game_mode)
    if game:
        await game.start(room_id)


async def _abandon_player(room_id: str, user_id: str):
    room = manager.rooms.get(room_id)
    if not room:
        return
    game = get_game(room.game_mode)
    if game:
        await game.on_abandon(room_id, user_id)


# Dependency Inversion: socket_manager oyun katmanını tanımaz;
# oyun katmanı kendini buradan enjekte eder.
manager.on_match_start = _start_game
manager.on_player_abandon = _abandon_player
