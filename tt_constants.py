"""Regler-Grenzen, feste Annahmen, Farben."""

WIN_LENGTH = 4
EMPTY = 0
PLAYER_ONE = 1  # beginnt immer, entspricht "Rot"
PLAYER_TWO = 2  # "Gelb"

PLAYER_NAMES = {PLAYER_ONE: "Rot", PLAYER_TWO: "Gelb"}
PLAYER_COLOURS = {PLAYER_ONE: "#d62728", PLAYER_TWO: "#f2c744"}
EMPTY_COLOUR = "#e5e5e5"

ORDER_NAIVE = "naiv"
ORDER_CENTER_FIRST = "mitte_zuerst"
ORDER_LABELS = {
    ORDER_NAIVE: "Naiv (Spalte 0, 1, 2, ... der Reihe nach)",
    ORDER_CENTER_FIRST: "Mitte zuerst",
}

# Live wählbare Brettgrößen - vorab gemessen (mit Transpositionstabelle, naive
# Reihenfolge). 5x5 dauert bereits 27,9s und ist deshalb NICHT live wählbar
# (nur Referenzpunkt) - alle anderen sieben Formen liegen unter 1,7s MIT
# Tabelle. "without_tt_ok" ist False für 4x5: OHNE Tabelle brauchte dieselbe
# Startstellung in alpha-beta-demo 43s - ein Live-Vergleich mit/ohne Tabelle
# würde also selbst einen 43s-Rechenlauf auslösen, genau auf dem Brett, das
# diese Demo doch gerade live nutzbar machen soll. Dort wird nur die
# vorab gemessene Zahl gezeigt, nie live nachgerechnet.
BOARD_OPTIONS = [
    {"rows": 3, "cols": 3, "label": "3 × 3", "without_tt_ok": True},
    {"rows": 4, "cols": 3, "label": "4 Zeilen × 3 Spalten", "without_tt_ok": True},
    {"rows": 3, "cols": 4, "label": "3 Zeilen × 4 Spalten", "without_tt_ok": True},
    {"rows": 4, "cols": 4, "label": "4 × 4", "without_tt_ok": True},
    {"rows": 5, "cols": 4, "label": "5 Zeilen × 4 Spalten", "without_tt_ok": True},
    {"rows": 3, "cols": 5, "label": "3 Zeilen × 5 Spalten", "without_tt_ok": True},
    {"rows": 4, "cols": 5, "label": "4 Zeilen × 5 Spalten", "without_tt_ok": False},
]
DEFAULT_BOARD_INDEX = 1  # 4x3

# Vorab gemessener Referenzpunkt, NICHT live wählbar.
MEASURED_TOO_SLOW = {"rows": 5, "cols": 5, "nodes": 8_190_870, "seconds": 27.9}

# Aus alpha-beta-demo (dieselbe Alpha-Beta-Suche OHNE Transpositionstabelle) -
# Referenz für den "wie viel bringt die Tabelle zusätzlich"-Vergleich.
ALPHA_BETA_BASELINE_NODES = {
    (3, 3): 213,
    (4, 3): 749,
    (3, 4): 2_826,
    (4, 4): 43_827,
    (5, 4): 849_868,
    (3, 5): 183_375,
    (4, 5): 12_480_661,
}
