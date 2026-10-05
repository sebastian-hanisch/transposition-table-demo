"""Unabhängiges Orakel für die Alpha-Beta-Suche mit/ohne Transpositionstabelle:
vollständiges Minimax mit Memoisierung auf unveränderlichen Brett-Tupeln und
Sieg-Prüfung per Volltabelle (statt inkrementellem Zobrist-Hash, Zug-Undo und
lokaler Sieg-Prüfung). Geprüft werden Spielwert UND bester Zug (muss den Wert
tatsächlich erreichen) für zufällige Teilstellungen beider Seiten am Zug."""

import functools
import random

import pytest

from tt_alphabeta import solve_position
from tt_constants import ORDER_CENTER_FIRST, ORDER_NAIVE
from tt_game import replay


def _wins(b, rows, cols, p):
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                if all(0 <= r + dr * k < rows and 0 <= c + dc * k < cols and b[r + dr * k][c + dc * k] == p for k in range(4)):
                    return True
    return False


def _make_oracle(rows, cols):
    def children(b, p):
        out = {}
        for c in range(cols):
            if b[0][c]:
                continue
            r = max(i for i in range(rows) if b[i][c] == 0)
            nb = tuple(tuple(p if (i, j) == (r, c) else b[i][j] for j in range(cols)) for i in range(rows))
            if _wins(nb, rows, cols, p):
                out[c] = 1 if p == 1 else -1
            elif all(nb[0]):
                out[c] = 0
            else:
                out[c] = value(nb, 3 - p)
        return out

    @functools.lru_cache(None)
    def value(b, p):
        vals = children(b, p).values()
        return max(vals) if p == 1 else min(vals)

    return value, children


SHAPES = [(2, 2), (2, 3), (3, 2), (3, 3), (4, 3), (3, 4), (5, 2), (2, 5), (1, 4)]


@pytest.mark.parametrize("rows,cols", SHAPES)
def test_value_and_best_move_match_independent_minimax(rows, cols):
    rng = random.Random(rows * 10 + cols)
    value, children = _make_oracle(rows, cols)
    checked = 0
    for _ in range(12):
        moves = [rng.randrange(cols) for _ in range(rng.randint(0, rows * cols - 1))]
        state = replay(rows, cols, moves)
        if state.is_terminal:
            continue
        b = tuple(tuple(r) for r in state.board)
        expected = value(b, state.player_to_move)
        kids = children(b, state.player_to_move)
        for order in (ORDER_NAIVE, ORDER_CENTER_FIRST):
            for use_tt in (False, True):
                board = [r[:] for r in state.board]
                result = solve_position(board, state.player_to_move, order=order, use_tt=use_tt)
                assert result.value == expected, (moves, order, use_tt)
                assert kids[result.best_column] == expected, (moves, order, use_tt)
                assert board == state.board  # Suche hinterlässt das Brett unverändert
        checked += 1
    assert checked > 0
