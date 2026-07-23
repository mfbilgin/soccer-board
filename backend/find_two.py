import random

from sqlalchemy.orm import Session

import models
from tictactoe import TicTacToeEngine


class FindTwoEngine:
    """'Takım & Ülke' veya 'Takım & Takım' kriter çiftini üretir ve bir
    oyuncu tahmininin bu kritere uyup uymadığını doğrular. Kriter üretimi
    TicTacToeEngine'in takım->oyuncu önbelleğini yeniden kullanır."""

    def __init__(self, db: Session):
        self.db = db
        self.tt = TicTacToeEngine(db)

    def _pick_team_team(self):
        for _ in range(200):
            a = random.choice(self.tt.popular_team_ids)
            a_players = self.tt.team_players.get(a, set())
            candidates = [t for t in self.tt.popular_team_ids if t != a and (self.tt.team_players.get(t, set()) & a_players)]
            if candidates:
                return a, random.choice(candidates)
        raise Exception("Takım-Takım kriteri üretilemedi.")

    def _pick_team_country(self):
        for _ in range(200):
            a = random.choice(self.tt.popular_team_ids)
            a_players = list(self.tt.team_players.get(a, set()))
            if not a_players:
                continue
            pid = random.choice(a_players)
            player = self.db.query(models.Player).filter(models.Player.id == pid).first()
            if player and player.nationality:
                return a, player.nationality
        raise Exception("Takım-Ülke kriteri üretilemedi.")

    def _team_label(self, team_id) -> str:
        t = self.db.query(models.Team).filter(models.Team.id == team_id).first()
        return (t.short_name if t and t.short_name else t.name) if t else "?"

    def generate_round(self) -> dict:
        kind = random.choice(["team_team", "team_country"])
        if kind == "team_team":
            a, b = self._pick_team_team()
            return {"kind": kind, "team_a_id": a, "team_a_name": self._team_label(a), "team_b_id": b, "team_b_name": self._team_label(b)}
        a, nationality = self._pick_team_country()
        return {"kind": kind, "team_a_id": a, "team_a_name": self._team_label(a), "country": nationality}

    def validate_guess(self, round_data: dict, player_id: int) -> bool:
        played_a = self.db.query(models.PlayerClubStat).filter(
            models.PlayerClubStat.player_id == player_id,
            models.PlayerClubStat.team_id == round_data["team_a_id"]
        ).first()
        if not played_a:
            return False

        if round_data["kind"] == "team_team":
            played_b = self.db.query(models.PlayerClubStat).filter(
                models.PlayerClubStat.player_id == player_id,
                models.PlayerClubStat.team_id == round_data["team_b_id"]
            ).first()
            return bool(played_b)

        player = self.db.query(models.Player).filter(models.Player.id == player_id).first()
        return bool(player and player.nationality == round_data["country"])
