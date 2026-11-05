# Proposal

## Why

Im Legacy-System kann das Fernlicht nach einem Programmende oder einem Serial-Fehler eingeschaltet bleiben. `yolov8.py` sendet beim Beenden kein `0`, behandelt nur SIGINT und gibt die serielle Verbindung nach dem ersten Schreibfehler dauerhaft auf. Fehlt der Adapter beim Start, läuft das Programm still weiter (ein Lauf über rund 2,8 Stunden mit 84.000 Frames lief so ohne Aktor). Fernlicht AUS ist der sichere Zustand, das System erfüllt das an diesen Stellen nicht.

Die Firmware des Mikrocontrollers blendet nach 1 bis 3 Sekunden ohne Kommando selbst ab. Das deckt Hard-Crashes, GPU-Hänger und Stromausfall ab. Offen bleiben die Pfade, auf denen der Prozess noch lebt oder kontrolliert endet.

## What Changes

- Auf jedem kontrollierten Beendigungspfad sendet das Programm vor dem Exit `0\n` an den Mikrocontroller: Strg-C, Taste `c`, unbehandelte Exception und neu SIGTERM.
- Das Programm sendet den Status mindestens alle 0,5 Sekunden (Heartbeat). Ist die letzte Frame-Entscheidung älter als 0,5 Sekunden (hängende Verarbeitung), sendet es `0` statt des veralteten Status. Ein hängender Prozess darf ein altes `1` nie am Leben halten.
- Nach einem Schreib- oder Verbindungsfehler baut das Programm die serielle Verbindung mit Wartezeit zwischen den Versuchen neu auf, statt dauerhaft aufzugeben. Währenddessen gilt Status 0 und das Log meldet ERROR.
- Fehlt der Adapter beim Start, läuft das Programm weiter, loggt einen deutlichen ERROR und versucht ebenfalls die Wiederverbindung.
- **BREAKING:** Die Legacy-Requirement „Kein Abschlusskommando beim Beenden" entfällt, und das Verhalten „dauerhafter Ausfall nach Schreibfehler" wird ersetzt.

## Capabilities

### New Capabilities
<!-- keine -->

### Modified Capabilities
- `actuator-control`: Kommandoprotokoll um Heartbeat-Intervall erweitert, Wiederverbindung statt dauerhaftem Ausfall, Abschlusskommando `0` beim Beenden, Start ohne Adapter mit Reconnect.
- `runtime-configuration`: Unbehandelte Fehler und Signale (SIGINT, SIGTERM) führen zum Abblenden vor dem Exit. Bei Fehlern endet das Programm mit einem Exit-Code ungleich 0, damit ein Dienst-Manager den Ausfall erkennen kann.

## Impact

- **Code:** `legacy/yolov8.py` (Referenz). Die Umsetzung erfolgt im neuen Code des Revivals, nicht im Legacy-Verzeichnis.
- **Hardware/Firmware:** Keine Änderung der Firmware. Voraussetzung ist der vorhandene Timeout von 1 bis 3 Sekunden. Das Protokoll (`1\n`, `0\n`, 9600 Baud) bleibt unverändert.
- **Betrieb:** Ein Dienst-Manager (zum Beispiel systemd) kann das Programm per SIGTERM beenden und erreicht dabei den sicheren Zustand.
- **Nicht im Umfang:** Mehrere Boxen auswerten (`multi-box-decision`), Standardgerät und GPU-Ausfall (`gpu-required`), Firmware-Änderungen.
