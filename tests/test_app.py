"""Rauchtests der Streamlit-Oberfläche per AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import tt_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=60)
    if setup is not None:
        setup(at)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Stellung" in h.value for h in at.subheader)


def test_every_board_option_renders():
    for index in range(len(C.BOARD_OPTIONS)):

        def setup(at, index=index):
            at.session_state["board_index_select"] = index
            at.session_state["moves"] = []

        _run(setup)


def test_toggling_tt_off_renders_and_shows_different_node_count():
    at_on = _run()
    on_metric = {m.label: m.value for m in at_on.metric}

    def setup(at):
        at.session_state["use_tt"] = False

    at_off = _run(setup)
    off_metric = {m.label: m.value for m in at_off.metric}
    assert on_metric["Durchsuchte Knoten"] != off_metric["Durchsuchte Knoten"]


def test_clicking_a_column_button_plays_a_move():
    at = _run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    assert drop_buttons
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.session_state["moves"]) == 1


def test_switching_board_size_resets_moves():
    def setup(at):
        at.session_state["board_index_select"] = 1
        at.session_state["moves"] = [0]

    at = _run(setup)
    at.radio(key="board_index_select").set_value(3)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == []


def test_permalink_restores_everything():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["board"] = "1"
    at.query_params["order"] = C.ORDER_CENTER_FIRST
    at.query_params["tt"] = "0"
    at.query_params["moves"] = "0,1"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["board_index_select"] == 1
    assert at.session_state["order_select"] == C.ORDER_CENTER_FIRST
    assert at.session_state["use_tt"] is False
    assert at.session_state["moves"] == [0, 1]


def test_4x5_without_tt_checkbox_is_locked_on():
    def setup(at):
        at.session_state["board_index_select"] = 6  # 4x5, without_tt_ok=False
        at.session_state["use_tt"] = False  # sollte von der App zurueck auf True gezwungen werden

    at = _run(setup)
    assert at.session_state["use_tt"] is True
    assert at.checkbox(key="use_tt").disabled is True


def test_4x5_after_a_move_does_not_show_a_misleading_baseline_ratio():
    # Echter Fund: der Vorab-Baseline-Wert gilt nur fuer die LEERE Startstellung
    # - nach einem Zug darf der Text keine "X-fach weniger"-Zahl mehr gegen
    # diesen (nicht mehr passenden) Basiswert zeigen.
    def setup(at):
        at.session_state["board_index_select"] = 6
        at.session_state["moves"] = [0]

    at = _run(setup)
    info_texts = " ".join(i.value for i in at.info)
    assert "kein direkter Vergleichswert ohne Tabelle für DIESE" in info_texts
    assert "-fach weniger)." not in info_texts


def test_permalink_does_not_get_clobbered_by_later_rerun():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["board"] = "1"
    at.run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == [0]
