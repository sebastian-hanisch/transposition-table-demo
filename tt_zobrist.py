"""Zobrist-Hashing: ein inkrementell fortgeführter Hash der Brettstellung.

Jeder belegten Zelle (Zeile, Spalte, Spieler) ist eine feste, zufällige 64-Bit-
Zahl zugeordnet; der Stellungs-Hash ist das XOR aller belegten Zellen. XOR ist
selbstinvers - derselbe Zug-Schritt macht das Setzen wie das Zurücknehmen
eines Steins rückgängig, ohne den ganzen Hash neu zu berechnen.

Wer am Zug ist gehört NICHT in den XOR-Hash, sondern wird als zweiter
Schlüsselteil mitgeführt (`(hash, player_to_move)`) - einfacher und genauso
korrekt wie ein eigener Seiten-Zufallswert.
"""

from __future__ import annotations

import random

from tt_game import Move

MAX_ROWS = 8
MAX_COLS = 8
_SEED = 20260929  # fest, damit Hashes über Testläufe reproduzierbar sind

_rng = random.Random(_SEED)
ZOBRIST = [[{1: _rng.getrandbits(64), 2: _rng.getrandbits(64)} for _ in range(MAX_COLS)] for _ in range(MAX_ROWS)]


def toggle(hash_value: int, move: Move, player: int) -> int:
    """Schaltet den Beitrag von `move`+`player` im Hash ein oder aus (XOR)."""
    return hash_value ^ ZOBRIST[move.row][move.column][player]


def board_hash(board: list[list[int]]) -> int:
    """Berechnet den Hash einmal von Grund auf (für den Start einer Suche)."""
    h = 0
    for r, row in enumerate(board):
        for c, value in enumerate(row):
            if value:
                h ^= ZOBRIST[r][c][value]
    return h
