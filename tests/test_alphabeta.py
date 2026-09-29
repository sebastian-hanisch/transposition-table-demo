"""Korrektheit (Kreuzprobe gegen alpha-beta-demo/minimax-demo) + der
Transpositions-Effekt, der den Kern dieses Stücks bildet."""

import pytest

from tt_constants import ORDER_CENTER_FIRST, ORDER_NAIVE, PLAYER_ONE, PLAYER_TWO
from tt_game import apply_move, empty_board
from tt_alphabeta import NodeCounter, solve_position


def test_1x1_board_is_a_trivial_draw():
    board = empty_board(1, 1)
    result = solve_position(board, PLAYER_ONE, use_tt=True)
    assert result.value == 0
    assert result.best_column == 0


def test_one_move_from_a_forced_win_is_detected():
    board = empty_board(4, 2)
    for col, player in [(0, PLAYER_ONE), (1, PLAYER_TWO)] * 3:
        apply_move(board, col, player)
    result = solve_position(board, PLAYER_ONE, use_tt=True)
    assert result.value == 1
    assert result.best_column == 0


@pytest.mark.parametrize("rows,cols", [(3, 3), (4, 3), (3, 4), (4, 4)])
def test_value_matches_previous_pieces_with_and_without_tt(rows, cols):
    # Kreuzprobe: dieselben Spielwerte wie in minimax-demo/alpha-beta-demo -
    # mit UND ohne Transpositionstabelle, beide muessen exakt uebereinstimmen.
    for use_tt in (False, True):
        board = empty_board(rows, cols)
        result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=use_tt)
        assert result.value == 0, (rows, cols, use_tt)


def test_transposition_table_reduces_node_count():
    board_without = empty_board(4, 4)
    without = solve_position(board_without, PLAYER_ONE, order=ORDER_NAIVE, use_tt=False)
    board_with = empty_board(4, 4)
    with_tt = solve_position(board_with, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True)
    assert with_tt.node_count < without.node_count
    assert with_tt.tt_hits > 0
    assert with_tt.tt_size > 0


def test_no_tt_means_no_hits_and_no_table():
    board = empty_board(4, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=False)
    assert result.tt_hits == 0
    assert result.tt_size == 0


def test_center_first_order_also_benefits_from_tt():
    board_without = empty_board(4, 3)
    without = solve_position(board_without, PLAYER_ONE, order=ORDER_CENTER_FIRST, use_tt=False)
    board_with = empty_board(4, 3)
    with_tt = solve_position(board_with, PLAYER_ONE, order=ORDER_CENTER_FIRST, use_tt=True)
    assert with_tt.node_count <= without.node_count


def test_result_is_deterministic_across_repeated_runs():
    # Der Zobrist-Zufallsgenerator ist fest geseedet (siehe tt_zobrist.py) -
    # wiederholte Läufe muessen exakt dieselbe Knotenzahl liefern.
    counts = set()
    for _ in range(3):
        board = empty_board(4, 3)
        counts.add(solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True).node_count)
    assert len(counts) == 1


def test_solve_is_pure_no_board_mutation():
    board = empty_board(4, 3)
    before = [row[:] for row in board]
    solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True)
    assert board == before


def test_node_counter_can_be_shared_across_calls():
    counter = NodeCounter()
    board = empty_board(3, 3)
    solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True, counter=counter)
    first = counter.count
    board2 = empty_board(3, 3)
    solve_position(board2, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True, counter=counter)
    assert counter.count > first
