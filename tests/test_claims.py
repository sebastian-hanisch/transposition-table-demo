"""Jede Zahl aus dem README wird hier gegen den tatsächlichen Code nachgerechnet."""

import pytest

from tt_constants import ORDER_NAIVE, PLAYER_ONE
from tt_game import empty_board
from tt_alphabeta import solve_position


@pytest.mark.parametrize(
    "rows,cols,use_tt,expected_nodes,expected_hits",
    [
        (3, 3, False, 213, 0),
        (3, 3, True, 158, 11),
        (4, 3, False, 749, 0),
        (4, 3, True, 524, 40),
        (3, 4, False, 2_826, 0),
        (3, 4, True, 1_120, 156),
        (4, 4, False, 43_827, 0),
        (4, 4, True, 10_661, 2_171),
    ],
)
def test_readme_node_counts(rows, cols, use_tt, expected_nodes, expected_hits):
    board = empty_board(rows, cols)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=use_tt)
    assert result.node_count == expected_nodes
    assert result.tt_hits == expected_hits


@pytest.mark.parametrize(
    "rows,cols,expected_nodes",
    [(5, 4, 86_851), (3, 5, 15_158), (4, 5, 509_530)],
)
def test_readme_larger_board_node_counts_with_tt(rows, cols, expected_nodes):
    board = empty_board(rows, cols)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True)
    assert result.node_count == expected_nodes


def test_readme_all_boards_are_draws():
    for rows, cols in [(3, 3), (4, 3), (3, 4), (4, 4), (5, 4), (3, 5)]:
        board = empty_board(rows, cols)
        result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True)
        assert result.value == 0
