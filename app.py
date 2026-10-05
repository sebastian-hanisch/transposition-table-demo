"""Transpositionstabelle: dieselbe Alpha-Beta-Suche, aber über einen
Zustands-DAG statt einen Baum - dieselbe Stellung über verschiedene Zugfolgen
wird nur einmal gelöst.

Kind-Stück von alpha-beta-demo (Adversarische-Suche-Linie).
"""

from __future__ import annotations

import streamlit as st

import tt_constants as C
from tt_alphabeta import NodeCounter, solve_position
from tt_evaluation import format_de_number, to_move_verdict, value_verdict
from tt_game import replay
from tt_pdf_export import build_pdf
from tt_presets import (
    PRESET_HELP,
    PRESETS,
    apply_preset,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from tt_visualization import board_figure, with_without_tt_figure

_de = format_de_number

st.set_page_config(page_title="Transpositionstabelle – Sebastian Hanisch", layout="wide")

st.title("🗂️ Transpositionstabelle: dieselbe Stellung nur einmal lösen")
st.markdown(
    """
    Der Spielbaum aus dem Elternstück (Alpha-Beta) ist eigentlich gar kein Baum: dieselbe Stellung lässt
    sich oft über **verschiedene Zugfolgen** erreichen (setzen beide Spieler dieselben Steine in dieselben Spalten, nur in anderer
    Reihenfolge, entsteht dasselbe Brett - solange in jeder Spalte die Farbfolge von unten nach oben gleich bleibt). Eine **Transpositionstabelle** erkennt das per
    **Zobrist-Hashing** und löst jede Stellung nur **einmal** – ein generelles Memoisierungs-Muster, wie
    ein Cache-Dict in einer dynamischen Programmierung. Am Ende der Seite: die 📐 Mathematische
    Formulierung.
    """
)

st.caption("🎯 Schnellstart")
preset_cols = st.columns(len(PRESETS))
for col, name in zip(preset_cols, PRESETS):
    col.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])
st.caption("🔗 Die URL merkt sich Brettgröße, Reihenfolge, Tabelle und Zugfolge (Permalink).")

load_permalink_settings()
init_session_state_defaults()


def _reset_moves() -> None:
    st.session_state["moves"] = []


def _on_board_change() -> None:
    st.session_state["moves"] = []
    if not C.BOARD_OPTIONS[st.session_state["board_index_select"]]["without_tt_ok"]:
        st.session_state["use_tt"] = True


with st.sidebar:
    st.header("⚙️ Einstellungen")
    order = st.radio(
        "Zugreihenfolge",
        options=[C.ORDER_NAIVE, C.ORDER_CENTER_FIRST],
        format_func=lambda o: C.ORDER_LABELS[o],
        key="order_select",
        on_change=_reset_moves,
    )
    board_index = st.radio(
        "Brettgröße",
        options=range(len(C.BOARD_OPTIONS)),
        format_func=lambda i: C.BOARD_OPTIONS[i]["label"],
        key="board_index_select",
        on_change=_on_board_change,
    )
    without_tt_ok = C.BOARD_OPTIONS[board_index]["without_tt_ok"]
    if not without_tt_ok and not st.session_state["use_tt"]:
        st.session_state["use_tt"] = True
    use_tt = st.checkbox(
        "Transpositionstabelle verwenden",
        key="use_tt",
        on_change=_reset_moves,
        disabled=not without_tt_ok,
        help=(
            "Auf dieser Brettgröße fest an: ohne Tabelle bräuchte schon die Startstellung 43s (alpha-beta-demo)."
            if not without_tt_ok
            else "Ausschalten zeigt dieselbe Suche wie in alpha-beta-demo, ohne jede Wiederverwendung."
        ),
    )
    if st.button("↺ Neues Spiel", use_container_width=True):
        st.session_state["moves"] = []
        st.rerun()

board_spec = C.BOARD_OPTIONS[board_index]
rows, cols = board_spec["rows"], board_spec["cols"]
moves: list[int] = [m for m in st.session_state["moves"] if 0 <= m < cols]
sync_query_params(board_index, order, use_tt, moves)


@st.cache_data(show_spinner="Durchsuche ...")
def _replay_and_solve(rows: int, cols: int, moves: tuple[int, ...], order: str, use_tt: bool):
    state = replay(rows, cols, list(moves))
    if state.is_terminal:
        return state, None
    counter = NodeCounter()
    result = solve_position([row[:] for row in state.board], state.player_to_move, order=order, use_tt=use_tt, counter=counter)
    return state, result


@st.cache_data(show_spinner="Vergleiche mit/ohne Tabelle ...")
def _with_without(rows: int, cols: int, moves: tuple[int, ...], order: str, without_tt_ok: bool):
    state = replay(rows, cols, list(moves))
    if state.is_terminal:
        return None, None
    if not without_tt_ok:
        # Ohne Tabelle bräuchte schon die Startstellung 43s (alpha-beta-demo,
        # dort deshalb nicht live wählbar) - nie live nachrechnen, siehe
        # tt_constants.BOARD_OPTIONS. Nur für die UNGESPIELTE Startstellung
        # gibt es einen vorab gemessenen Wert (moves leer).
        if not moves:
            return C.ALPHA_BETA_BASELINE_NODES.get((rows, cols)), None
        return None, None
    without = solve_position([row[:] for row in state.board], state.player_to_move, order=order, use_tt=False)
    with_tt = solve_position([row[:] for row in state.board], state.player_to_move, order=order, use_tt=True)
    return without.node_count, with_tt.node_count


state, result = _replay_and_solve(rows, cols, tuple(moves), order, use_tt)

st.subheader("Stellung")
board_col, info_col = st.columns([2, 1])

with board_col:
    best_col = result.best_column if result is not None else None
    fig = board_figure(state.board, state.last_move, state.winner, best_col)
    st.plotly_chart(fig, use_container_width=True, key="board_chart")

    if not state.is_terminal:
        click_cols = st.columns(cols)
        for c, click_col in enumerate(click_cols):
            full_column = state.board[0][c] != C.EMPTY
            label = f"⬇ {c}" + (" ★" if c == best_col else "")
            if click_col.button(label, key=f"drop_{c}", disabled=full_column, use_container_width=True):
                st.session_state["moves"] = moves + [c]
                st.rerun()

with info_col:
    if state.is_terminal:
        if state.winner is not None:
            st.success(f"Spiel beendet: {C.PLAYER_NAMES[state.winner]} hat gewonnen.")
        else:
            st.info("Spiel beendet: Remis (Brett voll).")
    else:
        st.metric("Am Zug", C.PLAYER_NAMES[state.player_to_move])
        st.metric("Durchsuchte Knoten", _de(result.node_count))
        if use_tt:
            st.caption(f"Davon per Tabelle wiederverwendet: {_de(result.tt_hits)} (Tabellengröße: {_de(result.tt_size)}).")
        verdict = to_move_verdict(result.value, state.player_to_move)
        if "erzwingen" in verdict and "nicht mehr" not in verdict:
            st.success(verdict)
        elif "verliert" in verdict:
            st.warning(verdict)
        else:
            st.info(verdict)
        st.caption("★ = gefundene optimale Spalte (garantiert exakt, siehe 📐 unten).")

        pdf_bytes = build_pdf(rows, cols, moves, order, use_tt, state.player_to_move, result.value, result.node_count, result.tt_hits, best_col)
        st.download_button("📄 Analyse als PDF", data=pdf_bytes, file_name="transposition_analyse.pdf", mime="application/pdf")

st.markdown("---")
st.subheader("🔬 Wie viel bringt die Tabelle zusätzlich?")
if state.is_terminal:
    st.info("Spiel bereits beendet - kein weiterer Suchbaum zu vergleichen.")
elif not board_spec["without_tt_ok"]:
    baseline = C.ALPHA_BETA_BASELINE_NODES.get((rows, cols))
    if not moves:
        st.info(
            f"Auf dieser Brettgröße wird 'ohne Tabelle' nie live nachgerechnet (schon die Startstellung "
            f"bräuchte 43s, siehe alpha-beta-demo) - nur der vorab gemessene Wert für die Startstellung: "
            f"**{_de(baseline)}** Knoten ohne Tabelle vs. **{_de(result.node_count)}** Knoten mit Tabelle "
            f"(**{_de(baseline / result.node_count, 1)}**-fach weniger)."
        )
    else:
        st.info(
            f"Auf dieser Brettgröße wird 'ohne Tabelle' nie live nachgerechnet (schon die Startstellung "
            f"bräuchte 43s, siehe alpha-beta-demo). Für die Startstellung gemessen: **{_de(baseline)}** "
            f"Knoten ohne Tabelle. Diese Stellung (nach {len(moves)} Zug/Zügen) braucht mit Tabelle "
            f"**{_de(result.node_count)}** Knoten - kein direkter Vergleichswert ohne Tabelle für DIESE "
            f"konkrete Stellung verfügbar."
        )
else:
    without_nodes, with_nodes = _with_without(rows, cols, tuple(moves), order, board_spec["without_tt_ok"])
    st.plotly_chart(with_without_tt_figure(without_nodes, with_nodes), use_container_width=True, key="compare_chart")
    if with_nodes:
        factor = without_nodes / with_nodes
        st.success(
            f"Ohne Tabelle: **{_de(without_nodes)}** Knoten. Mit Tabelle: **{_de(with_nodes)}** Knoten – "
            f"das **{_de(factor, 1)}**-fache weniger, obendrauf auf das, was Alpha-Beta allein schon spart."
        )

st.subheader("🔬 Wächst der Effekt mit der Brettgröße?")
st.markdown(
    """
    Größere Bretter haben nicht nur mehr Stellungen, sondern auch **proportional mehr** Wege, dieselbe
    Stellung zu erreichen – der Tabellen-Effekt sollte deshalb mit der Brettgröße zunehmen. Gemessen
    (naive Reihenfolge, ab dem leeren Brett):
    """
)
@st.cache_data(show_spinner="Messe den Tabellen-Effekt über alle Brettgrößen ...")
def _growth_table() -> list[str]:
    rows_cols = [(3, 3), (4, 3), (3, 4), (4, 4), (5, 4), (3, 5), (4, 5)]
    lines = []
    for r, c in rows_cols:
        wo = C.ALPHA_BETA_BASELINE_NODES[(r, c)]
        wi_state = replay(r, c, [])
        wi = solve_position(
            [row[:] for row in wi_state.board], wi_state.player_to_move, order=C.ORDER_NAIVE, use_tt=True
        ).node_count
        lines.append(f"- {r}×{c}: ohne {_de(wo)}, mit {_de(wi)} ({_de(wo / wi, 1)}-fach weniger)")
    return lines


st.markdown("\n".join(_growth_table()))
st.caption(
    f"Referenz (nicht live wählbar): 5×5 braucht selbst mit Tabelle noch "
    f"{_de(C.MEASURED_TOO_SLOW['nodes'])} Knoten ({_de(C.MEASURED_TOO_SLOW['seconds'], 1)}s)."
)

st.markdown("---")
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
    - **Kein Tiefen-Tracking nötig, aber ein echter Verzicht anderswo.** Diese Demo löst immer bis zum
      Spielende durch (kein Zeitlimit) - ein gespeicherter Wert ist deshalb immer vollständig, nie ein
      Zwischenstand. Echte Engines mit Zeitlimit müssen zusätzlich die Such-TIEFE je Tabelleneintrag
      mitführen (hier bewusst weggelassen, siehe „Bewusst nicht umgesetzt“).
    - **Die Tabelle wird pro Suche neu aufgebaut**, nicht über mehrere Züge hinweg mitgeführt - eine echte
      Partie-Engine würde die Tabelle auch nach dem eigenen Zug behalten (weiterer, hier nicht gebauter
      Gewinn).
    - **Speicher statt Zeit.** Die Tabelle wächst mit der Stellungszahl (auf 4×5 über 300.000 Einträge,
      siehe README) - ein echter Kompromiss, kein reiner Gewinn.
    """
)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
        Zobrist-Hashing: jeder belegten Zelle $(r, c, \text{Spieler})$ ist eine feste Zufallszahl
        $z_{r,c,p}$ zugeordnet, der Stellungs-Hash ist

        $$
        h(s) = \bigoplus_{(r,c,p) \in s} z_{r,c,p}
        $$

        (XOR über alle belegten Zellen). Weil XOR selbstinvers ist, macht derselbe Schritt das Setzen wie
        das Zurücknehmen eines Steins rückgängig - der Hash wird inkrementell mitgeführt, nie neu
        berechnet. Die Transpositionstabelle speichert zu jedem Schlüssel $(h(s), \text{Spieler})$ den
        gefundenen Wert und ob er EXAKT ist oder nur eine Schranke (Alpha-Beta-Fensterlogik, wie im
        Eltern-Stück) - ein zweiter Besuch derselben Stellung schlägt direkt nach, statt neu zu suchen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Adversarische Suche: Minimax bis Selbstspiel](https://sebastianhanisch.net/konzepte-adversarische-suche.html)."
)
