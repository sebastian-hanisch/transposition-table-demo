# Transpositionstabelle: dieselbe Stellung nur einmal lösen

Kind-Stück von **[alpha-beta-demo](https://github.com/sebastian-hanisch/alpha-beta-demo)** (selbst Kind von
**[minimax-demo](https://github.com/sebastian-hanisch/minimax-demo)**, Wurzel der Adversarische-Suche-Linie).
Vehikel: dasselbe Mini-Vier-Gewinnt, dasselbe Brettmodell (`tt_game.py` ist eine wortgleiche Kopie von
`ab_game.py`/`mm_game.py`).

## Warum dieses Problem

Der Spielbaum aus dem Elternstück ist eigentlich gar kein Baum: dieselbe Stellung lässt sich oft über
**verschiedene Zugfolgen** erreichen (Spalte A dann B ergibt dasselbe Brett wie B dann A, solange sich beide
Züge nicht überschneiden). Eine **Transpositionstabelle** erkennt das per **Zobrist-Hashing** und löst jede
Stellung nur einmal – ein generelles Memoisierungs-Muster, wie ein Cache-Dict in einer dynamischen
Programmierung.

## Modell

Identisch zu alpha-beta-demo (Board, Zugmechanik, Alpha-Beta-Suche). Neu: ein inkrementell fortgeführter
Zobrist-Hash (`tt_zobrist.py`) und eine Transpositionstabelle, die zu jedem Schlüssel `(hash, Spieler)` den
gefundenen Wert und ob er exakt oder nur eine Schranke ist speichert (Alpha-Beta-Fensterlogik).

## Methodik

Kein Tiefen-Tracking wie in echten Engines nötig: diese Demo löst immer bis zum Spielende durch (kein
Zeitlimit, keine Tiefenbegrenzung) – ein gespeicherter Wert ist deshalb immer der vollständige, endgültige
Wert der Stellung, nie ein Zwischenstand einer flacheren Suche. Die Tabelle wird pro Suche neu aufgebaut
(siehe „Ehrliche Grenzen").

## Befunde (gemessen, keine Behauptungen)

Alle Werte mit der tatsächlich ausgelieferten Suche gemessen (`tests/test_claims.py`), naive Reihenfolge,
ab dem leeren Brett:

| Brett | ohne Tabelle (= alpha-beta-demo) | mit Tabelle | Faktor |
|---|---|---|---|
| 3×3 | 213 | 158 | 1,3× |
| 4×3 | 749 | 524 | 1,4× |
| 3×4 | 2.826 | 1.120 | 2,5× |
| 4×4 | 43.827 | 10.661 | 4,1× |
| 5×4 | 849.868 | 86.851 | 9,8× |
| 3×5 | 183.375 | 15.158 | 12,1× |
| 4×5 | 12.480.661 | 509.530 | 24,5× |

- **Der Effekt wächst mit der Brettgröße** – von 1,3× auf 3×3 bis 24,5× auf 4×5. Größere Bretter haben
  nicht nur mehr Stellungen, sondern auch proportional mehr Wege, dieselbe Stellung zu erreichen.
- **4×5 wird dadurch erstmals live nutzbar.** In alpha-beta-demo brauchte diese Startstellung 43 s (zu
  langsam für die Demo dort) – hier nur noch 509.530 Knoten in gut 1,6 s.
- **Referenzpunkt 5×5** (nicht live wählbar): selbst mit Tabelle noch 8.190.870 Knoten (27,9 s).

## Ehrliche Grenzen

- **Kein öffentlicher Referenzlöser** für diese Nicht-Standardgrößen – Korrektheit über Kreuzprobe gegen
  die in minimax-demo/alpha-beta-demo gemessenen Spielwerte abgesichert (`tests/test_alphabeta.py`), mit
  UND ohne Tabelle.
- **Die Tabelle wird pro Suche neu aufgebaut**, nicht über mehrere Züge hinweg mitgeführt – eine echte
  Partie-Engine würde die Tabelle auch nach dem eigenen Zug behalten (weiterer, hier nicht gebauter Gewinn).
- **Speicher statt Zeit.** Die Tabelle wächst mit der Stellungszahl (auf 4×5 über 300.000 Einträge) – ein
  echter Kompromiss, kein reiner Gewinn.
- **Auf 4×5 wird „ohne Tabelle" nie live nachgerechnet** (43 s schon für die Startstellung) – dort steht
  nur der vorab gemessene Startwert, nach einem Zug gibt es ehrlich keinen Live-Vergleichswert mehr
  (echter Bug beim Bau: die App verglich anfangs die aktuelle, bereits reduzierte Knotenzahl fälschlich
  gegen den Startwert-Baseline und zeigte einen irreführenden Faktor – jetzt korrekt nur für die
  Startstellung selbst gezeigt).

## Tests

55 Tests (`pytest tests/ -v`): Brettmechanik, Zobrist-Hashing (inkrementell = neu berechnet, Transpositionen
ergeben identische Hashes), Suchalgorithmus (Kreuzprobe gegen alpha-beta-demo, mit/ohne Tabelle), PDF-Export,
Visualisierung, Streamlit-Rauchtests (AppTest: jede Brettgröße, TT-Checkbox auf 4×5 fest verriegelt,
Permalink-Rundlauf). Drei echte Bugs beim Bau gefunden+gefixt:

1. Der „Wie viel bringt die Tabelle"-Vergleich löste auf 4×5 versehentlich eine LIVE 43-Sekunden-Suche ohne
   Tabelle aus, sobald diese Brettgröße ausgewählt wurde – genau auf dem Brett, das die Demo doch gerade
   nutzbar machen soll. Fix: `without_tt_ok`-Flag pro Brettgröße, die Tabelle bleibt auf 4×5 fest an
   (Checkbox gesperrt), der Vergleich nutzt dort nur den vorab gemessenen Wert.
2. Ein Tippfehler bei den Anführungszeichen (deutsches „…" gemischt mit geradem ") brach die Python-Syntax
   der App komplett.
3. Nach einem Zug auf 4×5 verglich die App die bereits reduzierte aktuelle Knotenzahl fälschlich gegen den
   nur für die LEERE Startstellung gültigen Vorab-Wert – ein irreführender „X-fach weniger"-Faktor ohne
   Aussagekraft. Fix: dieser Vergleich erscheint jetzt nur noch für die tatsächliche Startstellung.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `tt_constants.py` | Brettgrößen, Reihenfolgen, gemessene Referenzwerte |
| `tt_game.py` | Brettmechanik (Kopie von alpha-beta-demo) |
| `tt_zobrist.py` | Zobrist-Hashing |
| `tt_alphabeta.py` | Alpha-Beta-Suche + Transpositionstabelle |
| `tt_evaluation.py` | Verdikt-Texte, Zahlenformatierung |
| `tt_visualization.py` | Plotly-Brett und Mit/Ohne-Vergleich |
| `tt_presets.py` | Presets, Permalink, Session-Defaults |
| `tt_pdf_export.py` | PDF-Export |

## Bewusst nicht umgesetzt

- Tiefen-Tracking je Tabelleneintrag (nur relevant mit Zeitlimit/iterativer Vertiefung – hier löst jede
  Suche immer bis zum Spielende durch).
- Tabelle über mehrere Züge hinweg beibehalten (echter zusätzlicher Gewinn, aber eigener Cache-Invalidierungs-
  Aufwand – nicht der Kern dieses Stücks).

## Lokal ausführen

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.
