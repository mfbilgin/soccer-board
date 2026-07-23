import random
import re
from collections import defaultdict

from sqlalchemy.orm import Session
from unidecode import unidecode

import models

_CACHE = {}


class InitialsGuessEngine:
    """Bilinen adı belirli bir harfle başlayıp belirli bir harfle biten
    oyuncuları bulur. (start_letter, end_letter) -> [player_id,...] önbelleği
    üzerinden, herhangi bir 5x5 harf kombinasyonunun tamamının çözülebilir
    olduğu bir havuz çifti üretir."""

    def __init__(self, db: Session):
        self.db = db
        if not _CACHE:
            self._initialize()
        self.pair_players = _CACHE['pair_players']
        self.start_players = _CACHE['start_players']
        self.end_players = _CACHE['end_players']

    def _initialize(self):
        players = self.db.query(models.Player.id, models.Player.known_as).filter(models.Player.known_as.isnot(None)).all()
        pair_players = defaultdict(list)
        start_players = defaultdict(list)
        end_players = defaultdict(list)

        for pid, name in players:
            clean = re.sub(r'[^A-Za-z]', '', unidecode(name or ''))
            if len(clean) < 2:
                continue
            s, e = clean[0].upper(), clean[-1].upper()
            pair_players[(s, e)].append(pid)
            start_players[s].append(pid)
            end_players[e].append(pid)

        _CACHE['pair_players'] = pair_players
        _CACHE['start_players'] = start_players
        _CACHE['end_players'] = end_players

    def generate_letter_pools(self) -> dict:
        """Her ikisi de 5 harf iceren start_pool/end_pool doner - hangi
        kombinasyon secilirse secilsin en az bir gercek oyuncu vardir."""
        top_starts = sorted(self.start_players.keys(), key=lambda s: len(self.start_players[s]), reverse=True)[:10]
        top_ends = sorted(self.end_players.keys(), key=lambda e: len(self.end_players[e]), reverse=True)[:10]

        for _ in range(300):
            starts = random.sample(top_starts, min(5, len(top_starts)))
            ends = random.sample(top_ends, min(5, len(top_ends)))
            if all(self.pair_players.get((s, e)) for s in starts for e in ends):
                return {"start_pool": starts, "end_pool": ends}

        raise Exception("Initials Guess harf havuzu üretilemedi.")

    def validate_guess(self, start_letter: str, end_letter: str, player_id: int) -> bool:
        candidates = self.pair_players.get(((start_letter or '').upper(), (end_letter or '').upper()), [])
        return player_id in candidates

    def get_example_answer(self, start_letter: str, end_letter: str):
        candidates = self.pair_players.get(((start_letter or '').upper(), (end_letter or '').upper()), [])
        if not candidates:
            return None
        p = self.db.query(models.Player).filter(models.Player.id == candidates[0]).first()
        return p.known_as if p else None
