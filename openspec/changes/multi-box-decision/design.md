# Design

## Context

Die Baseline-Spec `high-beam-decision` bewertet nur die erste Box (Geometrie) und die zuletzt durchlaufene Box (Konfidenz). Motivation steht in `proposal.md`. Voraussetzung ist `modular-pipeline`: `decide(state, boxes, now_seconds) -> (state, status)` als reine Funktion.

Messungen auf `hba1` (Replay über die Logs `17183156523746762.log` und `17199608122269757.log`, zusammen 44.836 Frames, 286 Statuswechsel):

- Der Nachbau der **alten** Logik reproduziert den geloggten `HBA Status` in jedem Frame (0 Abweichungen).
- Die **neue** Logik liefert in jedem Frame denselben Status wie die alte. Der Fehlerfall kommt in den echten Daten nicht vor.

## Goals / Non-Goals

**Goals:**
- Alle Boxen eines Frames fließen in die Entscheidung ein.
- Die neue Logik blendet nie weniger ab als die alte, belegt durch Replay, Property-Test und Beweis.

**Non-Goals:**
- Keine Gewichtung nach Klasse, Größe oder Abstand, keine Änderung von Haltezeit oder Drosselung.
- Keine Änderung des Auto-Labels in der Datensammlung.

## Decisions

### 1. Relevanz je Box, Aktualisierung bei „irgendeine relevant"

Ein Frame aktualisiert den Zeitpunkt der letzten Detektion, wenn mindestens eine Box Geometrie und Konfidenz erfüllt. Die Drosselung (`lastDetectTimer1`, einmal pro Sekunde) bleibt unverändert und hängt nur davon ab, ob der Frame überhaupt Boxen enthielt.

*Alternative:* Nur die größte Box prüfen. Verworfen, weil „größte" eine neue Annahme einführt, die niemand geprüft hat. „Irgendeine" ist die konservative Lesart.

### 2. Nie weniger Abblenden: Beweisskizze

Sei `rel(b)` die Relevanz einer Box. Die alte Logik fragt `rel(erste)`, die neue `any(rel)`. Daraus folgt `rel(erste) ⇒ any(rel)`. `lastDetectTimer1` ändert sich in beiden Logiken identisch (nur abhängig von „Frame hat Boxen"). Damit darf die neue Logik jede Aktualisierung von `lastDetectTimer`, die die alte ausführt, ebenfalls ausführen. Per Induktion gilt in jedem Frame `neu.lastDetectTimer >= alt.lastDetectTimer`, also `neu.status <= alt.status`.

Voraussetzung ist, dass die Konfidenzprüfung für die erste Box in beiden Logiken gleich ausfällt. Der Detektor filtert bereits mit demselben Schwellwert, die Prüfung ist praktisch wirkungslos. Der Property-Test deckt den Fall ab, indem er Konfidenzen oberhalb des Schwellwerts erzeugt.

### 3. Drei Testebenen

```
1. Nachbau alt == geloggt     echte Logs, exakt, ohne Toleranz
2. neu <= alt                 echte Logs (Replay) + Property-Test mit Zufallsfolgen
3. Konstruierte Frames        erste Box irrelevant, zweite relevant -> abblenden
```

Ebene 1 schafft Vertrauen in die Baseline. Ebene 2 belegt „keine Regression". Ebene 3 zeigt als Einzige, dass der Fix wirkt, weil die echten Logs den Fall nie enthalten.

### 4. Testdaten als kompakte Auszüge

Die rohen Logs (rund 80 MB) bleiben auf `hba1`. Ins Repo kommen aus den beiden Logs mit Detektionen kompakte Auszüge als `tests/data/*.jsonl.gz`, eine Zeile pro Frame: Startzeit, Zeitpunkt der Detektion, Zeitpunkt des Status, Boxen (`x1,y1,x2,y2`, Klasse, Konfidenz), geloggter Status. Erwartet wird deutlich unter 1 MB. Der Lauf ohne Detektionen (84.770 Frames) trägt nichts bei und bleibt draußen.

Das Extraktionsskript liegt unter `tools/extract_replay.py`, damit die Auszüge reproduzierbar sind. Es wird auf `hba1` gegen die Roh-Logs ausgeführt.

### 5. Keine Toleranz nötig

Der Nachbau trifft den geloggten Status exakt, weil das Log die verwendeten Zeitstempel enthält. Eine Toleranz an Sekundengrenzen entfällt.

## Risks / Trade-offs

- **Die echten Logs enthalten den Fehlerfall nicht** → Ebene 3 mit konstruierten Frames und der Property-Test decken ihn ab. Der Replay allein wäre ein Scheinbeweis.
- **Mehr Boxen sorgen für längeres Abblenden und damit weniger Fernlicht** → Gewollt (sicherer Zustand). Im Replay zeigt sich kein Unterschied. Sollte er später auftreten, wird er als bewusste Folge dokumentiert.
- **Auszüge weichen vom Roh-Log ab** → Das Extraktionsskript prüft Frame-Anzahl und Statuswechsel gegen die Roh-Logs und gibt Prüfsummen aus.

## Migration Plan

1. Extraktionsskript auf `hba1` ausführen, Auszüge ins Repo übernehmen.
2. Tests auf dem Mac schreiben und laufen lassen, danach auf `hba1`.
3. Entscheidungsmodul umstellen. Die Legacy-Eigenheit wird entfernt.

Rollback: Rückkehr zum Stand von `modular-pipeline` (nur erste Box).

## Open Questions

- Keine.
