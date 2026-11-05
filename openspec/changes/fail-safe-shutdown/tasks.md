# Tasks

Annahme zum Code-Layout: Python-Paket `src/hba/`, Tests mit pytest unter `tests/`. Die endgültige Modulaufteilung legt der spätere Change `modular-pipeline` fest.

## 1. Projektgerüst

- [ ] 1.1 Paket `src/hba/` und `tests/` mit `pyproject.toml` (Abhängigkeiten pyserial, pytest) anlegen und verifizieren, dass `pytest` ohne Fehler durchläuft

## 2. Aktor-Sender (`actuator-control`)

- [ ] 2.1 `ActuatorLink` mit `set_status(0|1)` und Sender-Thread (Takt 0,2 s) in `src/hba/actuator.py` implementieren und per Pseudo-Terminal-Test verifizieren, dass `1\n` ankommt und zwischen zwei Kommandos höchstens 0,5 s liegen
- [ ] 2.2 Staleness-Regel (Entscheidung älter als 0,5 s sendet `0`) einbauen und verifizieren: nach `set_status(1)` und 0,6 s ohne Update kommt `0\n` und danach nie wieder `1\n`
- [ ] 2.3 Wiederverbindung (Versuch alle 2 s, ERROR einmal beim Verlust, Erinnerung höchstens alle 30 s, INFO bei Wiederherstellung) einbauen und verifizieren: Gegenstelle schließen, neue Gegenstelle am selben Pfad öffnen, Kommandos kommen innerhalb von 5 s wieder an
- [ ] 2.4 Start ohne Adapter behandeln und verifizieren: Konstruktion mit nicht existierendem Pfad wirft nicht, loggt `configure_serial_connection: ERROR!`, Status gilt als 0 und verbindet, sobald das Gerät erscheint
- [ ] 2.5 Sender-Thread gegen eigene Fehler absichern und verifizieren: ein eingespeister Fehler wird geloggt und die Schleife läuft weiter

## 3. Lebenszyklus (`runtime-configuration`)

- [ ] 3.1 Idempotente `shutdown()` in `src/hba/lifecycle.py` implementieren (sendet `0\n`, leert den Puffer, schließt, `write_timeout` 0,5 s) und verifizieren: zweimal aufgerufen sendet sie genau einmal, ein blockierender Fake-Port verlängert das Beenden um höchstens 2 s
- [ ] 3.2 Handler für SIGINT, SIGTERM, Taste `c`, `sys.excepthook` und `atexit` auf `shutdown()` verdrahten und per Subprozess-Test verifizieren: SIGTERM und SIGINT liefern `0\n` und Exit-Code 0, eine unbehandelte Exception liefert `0\n` und Exit-Code ungleich 0
- [ ] 3.3 Zusammenspiel mit dem Firmware-Timeout in `docs/fail-safe.md` beschreiben (Pfade, SIGKILL, Messverfahren) und verifizieren, dass jede Zeile der Spec-Szenarien dort einem Pfad zugeordnet ist

## 4. Anbindung an die Hauptschleife

Voraussetzung: Es gibt eine Hauptschleife im neuen Code (siehe Change `modular-pipeline`). Ohne sie bleibt diese Gruppe offen.

- [ ] 4.1 Hauptschleife ruft pro Frame-Entscheidung `set_status` auf und verwirft vor der Freigabe einen Warm-up-Frame, verifiziert mit einem Test, in dem ein künstlicher Hänger der Hauptschleife (1 s) innerhalb von 0,7 s ein `0\n` am Pseudo-Terminal auslöst

## 5. Prüfung auf `hba1` mit Mikrocontroller

- [ ] 5.1 `kill -TERM` bei eingeschaltetem Fernlicht ausführen und verifizieren, dass das Relais sofort abfällt
- [ ] 5.2 `kill -STOP` ausführen, die Zeit bis zum Abblenden mit einer Stoppuhr messen und das Ergebnis als Firmware-Timeout in `docs/fail-safe.md` eintragen
- [ ] 5.3 Adapter im Betrieb ziehen und wieder stecken und verifizieren, dass das Fernlicht während des Ausfalls aus ist und danach wieder gesteuert wird

## Workflow follow-up

- Change nach dem Review archivieren (`/opsx:archive`), damit die Delta-Specs in `openspec/specs/` einfließen.
- Archiviertes Ergebnis prüfen: `openspec validate --specs --strict`.
