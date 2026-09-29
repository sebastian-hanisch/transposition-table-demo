"""Zobrist-Hashing: inkrementelle Fortführung muss mit einer Neuberechnung von
Grund auf übereinstimmen, und zwei verschiedene Zugfolgen zur selben Stellung
müssen denselben Hash ergeben (das ist der ganze Zweck der Technik)."""

from tt_constants import PLAYER_ONE, PLAYER_TWO
from tt_game import apply_move, empty_board, undo_move
from tt_zobrist import board_hash, toggle


def test_empty_board_hash_is_zero():
    board = empty_board(4, 3)
    assert board_hash(board) == 0


def test_incremental_toggle_matches_fresh_computation():
    board = empty_board(4, 3)
    h = board_hash(board)
    move = apply_move(board, 1, PLAYER_ONE)
    h = toggle(h, move, PLAYER_ONE)
    assert h == board_hash(board)


def test_toggle_twice_returns_to_original_hash():
    board = empty_board(4, 3)
    h0 = board_hash(board)
    move = apply_move(board, 1, PLAYER_ONE)
    h1 = toggle(h0, move, PLAYER_ONE)
    undo_move(board, move)
    h2 = toggle(h1, move, PLAYER_ONE)
    assert h2 == h0


def test_different_move_orders_reaching_the_same_board_hash_identically():
    # Spalte 0 dann 1 vs. Spalte 1 dann 0 (verschiedene Spieler je Zug, damit
    # beide Reihenfolgen wirklich dasselbe Brett ergeben) - eine echte
    # Transposition.
    board_a = empty_board(4, 3)
    h = board_hash(board_a)
    m1 = apply_move(board_a, 0, PLAYER_ONE)
    h = toggle(h, m1, PLAYER_ONE)
    m2 = apply_move(board_a, 1, PLAYER_TWO)
    h = toggle(h, m2, PLAYER_TWO)

    board_b = empty_board(4, 3)
    h2 = board_hash(board_b)
    m1b = apply_move(board_b, 1, PLAYER_TWO)
    h2 = toggle(h2, m1b, PLAYER_TWO)
    m2b = apply_move(board_b, 0, PLAYER_ONE)
    h2 = toggle(h2, m2b, PLAYER_ONE)

    assert board_a == board_b
    assert h == h2


def test_different_boards_have_different_hashes():
    board_a = empty_board(4, 3)
    apply_move(board_a, 0, PLAYER_ONE)
    board_b = empty_board(4, 3)
    apply_move(board_b, 1, PLAYER_ONE)
    assert board_hash(board_a) != board_hash(board_b)
