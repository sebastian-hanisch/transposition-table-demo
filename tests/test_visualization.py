"""Regressionstest gegen den in minimax-demo gefundenen scaleanchor+range-Bug."""

from tt_game import empty_board
from tt_visualization import board_figure, with_without_tt_figure


def test_board_figure_uses_autorange_not_explicit_range():
    board = empty_board(4, 3)
    fig = board_figure(board, None, None, 1)
    assert fig.layout.xaxis.autorange is True
    assert fig.layout.xaxis.range is None
    assert fig.layout.yaxis.autorange is True
    assert fig.layout.yaxis.range is None


def test_board_figure_cell_count_matches_board_size():
    board = empty_board(3, 4)
    fig = board_figure(board, None, None, None)
    assert len(fig.data[0].x) == 3 * 4


def test_with_without_figure_has_two_bars():
    fig = with_without_tt_figure(749, 524)
    assert len(fig.data[0].x) == 2
