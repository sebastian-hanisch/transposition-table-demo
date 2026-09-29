"""Alpha-Beta-Pruning + Transpositionstabelle (Zobrist-Hashing).

Kind-Stück von alpha-beta-demo. Dieselbe Alpha-Beta-Suche wie dort, zusätzlich
mit einer Transpositionstabelle: erreicht die Suche über eine ANDERE Zugfolge
dieselbe Stellung noch einmal (ein Zustands-DAG statt eines Baums), wird das
bereits gefundene Ergebnis wiederverwendet statt neu gesucht.

Kein Tiefen-Tracking wie in echten Engines nötig: diese Demo löst immer bis
zum Spielende durch (kein Zeitlimit, keine Tiefenbegrenzung) - ein gespeicherter
Wert ist deshalb immer der VOLLSTÄNDIGE, endgültige Wert der Stellung, nie nur
ein Zwischenstand einer flacheren Suche.
"""

from __future__ import annotations

from dataclasses import dataclass

from tt_constants import ORDER_CENTER_FIRST, ORDER_NAIVE, PLAYER_ONE
from tt_game import apply_move, check_win_at, is_full, legal_columns, other_player, undo_move
from tt_zobrist import board_hash, toggle

_NEG_INF, _POS_INF = -2, 2
EXACT, LOWER, UPPER = "exact", "lower", "upper"


@dataclass
class NodeCounter:
    count: int = 0
    tt_hits: int = 0


@dataclass
class SolveResult:
    value: int
    node_count: int
    best_column: int
    tt_hits: int
    tt_size: int


def _center_first_order(cols: list[int], width: int) -> list[int]:
    centre = (width - 1) / 2
    return sorted(cols, key=lambda c: abs(c - centre))


def _terminal_value(board, move, player) -> int | None:
    if check_win_at(board, move, player):
        return 1 if player == PLAYER_ONE else -1
    if is_full(board):
        return 0
    return None


def _ordered_columns(board, order: str) -> list[int]:
    cols = legal_columns(board)
    if order == ORDER_CENTER_FIRST:
        return _center_first_order(cols, len(board[0]))
    return cols


def _recurse(board, player, alpha, beta, h: int, counter: NodeCounter, order: str, table: dict | None) -> int:
    counter.count += 1
    original_alpha = alpha

    key = (h, player) if table is not None else None
    if table is not None and key in table:
        value, flag = table[key]
        if flag == EXACT:
            counter.tt_hits += 1
            return value
        if flag == LOWER:
            alpha = max(alpha, value)
        elif flag == UPPER:
            beta = min(beta, value)
        if alpha >= beta:
            counter.tt_hits += 1
            return value

    best = None
    for col in _ordered_columns(board, order):
        move = apply_move(board, col, player)
        h2 = toggle(h, move, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), alpha, beta, h2, counter, order, table)
        undo_move(board, move)
        if player == PLAYER_ONE:
            if best is None or value > best:
                best = value
            alpha = max(alpha, best)
        else:
            if best is None or value < best:
                best = value
            beta = min(beta, best)
        if alpha >= beta:
            break

    if table is not None:
        if best <= original_alpha:
            flag = UPPER
        elif best >= beta:
            flag = LOWER
        else:
            flag = EXACT
        table[key] = (best, flag)

    return best


def solve_position(board, player, order: str = ORDER_NAIVE, use_tt: bool = True, counter: NodeCounter | None = None) -> SolveResult:
    if counter is None:
        counter = NodeCounter()
    table: dict | None = {} if use_tt else None

    counter.count += 1
    h = board_hash(board)
    cols = _ordered_columns(board, order)
    alpha, beta = _NEG_INF, _POS_INF
    best_value = None
    best_col = cols[0] if cols else None
    for col in cols:
        move = apply_move(board, col, player)
        h2 = toggle(h, move, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), alpha, beta, h2, counter, order, table)
        undo_move(board, move)
        if player == PLAYER_ONE:
            if best_value is None or value > best_value:
                best_value, best_col = value, col
            alpha = max(alpha, best_value)
        else:
            if best_value is None or value < best_value:
                best_value, best_col = value, col
            beta = min(beta, best_value)
        if alpha >= beta:
            break

    return SolveResult(
        value=best_value,
        node_count=counter.count,
        best_column=best_col,
        tt_hits=counter.tt_hits,
        tt_size=len(table) if table is not None else 0,
    )
