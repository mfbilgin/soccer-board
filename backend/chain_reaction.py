import random
from typing import Optional, Set

from sqlalchemy.orm import Session

import models
from tictactoe import TicTacToeEngine


class ChainReactionEngine:
    """Oyuncu->Takım->Oyuncu zincirini yönetir. team_players/player_teams
    önbelleğini TicTacToeEngine ile paylaşır (aynı süreçte zaten yüklüyse
    tekrar hesaplanmaz)."""

    def __init__(self, db: Session):
        self.db = db
        self.tt = TicTacToeEngine(db)

    def pick_start_player(self, exclude: Optional[Set[int]] = None) -> dict:
        exclude = exclude or set()
        candidates = [pid for pid in self.tt.elite_player_ids if pid not in exclude]
        if not candidates:
            candidates = self.tt.elite_player_ids
        pid = random.choice(candidates)
        player = self.db.query(models.Player).filter(models.Player.id == pid).first()
        return {"id": pid, "name": player.known_as if player else "Bilinmeyen"}

    def get_valid_continuations(self, node_type: str, node_id: int, used_players: Set[int], used_teams: Set[int]) -> Set[int]:
        if node_type == "player":
            return self.tt.player_teams.get(node_id, set()) - used_teams
        return self.tt.team_players.get(node_id, set()) - used_players

    def validate_answer(self, prev_type: str, prev_id: int, answer_id: int, used_players: Set[int], used_teams: Set[int]) -> bool:
        return answer_id in self.get_valid_continuations(prev_type, prev_id, used_players, used_teams)

    def get_entity_name(self, node_type: str, node_id: int) -> str:
        if node_type == "player":
            p = self.db.query(models.Player).filter(models.Player.id == node_id).first()
            return p.known_as if p else "Bilinmeyen"
        t = self.db.query(models.Team).filter(models.Team.id == node_id).first()
        return (t.short_name if t and t.short_name else t.name) if t else "Bilinmeyen"
