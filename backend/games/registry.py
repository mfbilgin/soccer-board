"""game_mode kimliği -> GameMode nesnesi kaydı.

Open/Closed: yeni bir oyun modu eklemek için mevcut koda dokunmak gerekmez;
GameMode alt sınıfını @register ile işaretlemek yeterlidir.
"""
from typing import Dict, Optional

_REGISTRY: Dict[str, "GameMode"] = {}


def register(cls):
    """GameMode alt sınıfını, sunduğu tüm mod kimlikleriyle kaydeder."""
    instance = cls()
    for mode in instance.modes:
        _REGISTRY[mode] = instance
    return cls


def get_game(mode: str) -> Optional["GameMode"]:
    return _REGISTRY.get(mode)
