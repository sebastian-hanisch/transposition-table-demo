"""Regressionstest: aufeinanderfolgende multi_cell-Aufrufe dürfen nicht
crashen, keine fpdf2-Crash-Zeichen in PDF-gebundenen Strings."""

from tt_constants import ORDER_NAIVE, PLAYER_ONE
from tt_game import empty_board
from tt_alphabeta import solve_position
from tt_pdf_export import build_pdf


def test_build_pdf_does_not_crash():
    board = empty_board(4, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=True)
    pdf_bytes = build_pdf(
        4, 3, [], ORDER_NAIVE, True, PLAYER_ONE, result.value, result.node_count, result.tt_hits, result.best_column
    )
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_build_pdf_without_tt_does_not_crash():
    board = empty_board(4, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, use_tt=False)
    pdf_bytes = build_pdf(
        4, 3, [], ORDER_NAIVE, False, PLAYER_ONE, result.value, result.node_count, result.tt_hits, result.best_column
    )
    assert pdf_bytes.startswith(b"%PDF")
