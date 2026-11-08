# Proposal

## Why

Die Fernlicht-Entscheidung im Legacy-Code prüft nur die **erste** gemeldete Box (Breite und obere Kante) und die Konfidenz der **zuletzt** durchlaufenen Box. Ist ein zweites Fahrzeug relevant, das erste aber nicht, wird das Fernlicht trotz sichtbaren Gegenverkehrs freigegeben. Das ist der gefährlichste Fehlerfall des Systems.

Die echten Fahrt-Logs (zwei Läufe, rund 45.000 Frames, 7.591 Frames mit Detektion, 490 davon mit mindestens zwei Boxen) zeigen **keinen** solchen Fall. Ultralytics sortiert Boxen nach Konfidenz, die erste ist meist das nächste Fahrzeug. Der Fehler ist also real, hat sich aber nie ausgewirkt. Die Konfidenzprüfung ist praktisch wirkungslos, weil das Modell bereits bei 0,4 filtert.

## What Changes

- Die Entscheidung wertet **alle** Boxen eines Frames aus: Jede relevante Box mit ausreichender Konfidenz verlängert die Abblendphase.
- Alles Übrige bleibt identisch: Haltezeit 3 s, Drosselung auf eine Aktualisierung pro Sekunde, sofortiges Abblenden, verzögertes Aufblenden.
- Der Nachweis läuft über drei Ebenen: **Replay mit den echten Logs** (Nachbau der alten Logik reproduziert den geloggten `HBA Status`, die neue Logik nie Status 1 wo die alte 0 lieferte), ein **Property-Test** mit Zufallsfolgen und **konstruierte Frames** für den Fehlerfall, den die echten Logs nie enthalten.
- **BREAKING:** Die Legacy-Requirement „Bewertungsgrundlage ist die erste Box (Legacy-Eigenheit)" entfällt.

## Capabilities

### New Capabilities
<!-- keine -->

### Modified Capabilities
- `high-beam-decision`: Auswertung über alle Boxen statt nur der ersten. Die Legacy-Eigenheit wird ersetzt.

## Impact

- **Code:** Entscheidungsmodul aus `modular-pipeline`, plus Replay-Test.
- **Testdaten:** Kompakte Auszüge der beiden Logs mit Detektionen (`tests/data/*.jsonl.gz`, unter 1 MB), erzeugt auf `hba1` aus `~/HBA/logs/`. Die rund 80 MB Roh-Logs bleiben dort. Eine Zeittoleranz ist nicht nötig: Der Nachbau der alten Logik reproduziert den geloggten Status exakt (0 Abweichungen in 44.836 Frames).
- **Voraussetzung:** `modular-pipeline` (Entscheidung als reine Funktion mit eingespeister Uhr).
- **Nicht im Umfang:** Gewichtung nach Klasse, Größe oder Abstand, Änderung der Haltezeit, nur die erste Box ins Auto-Label zu schreiben (gehört zu `data-collection`).
