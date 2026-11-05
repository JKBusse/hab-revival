# Proposal

## Why

Das Legacy-System ist ein einziges Skript (`legacy/yolov8.py`, ~12 KB), in dem Aufnahme, Erkennung, Entscheidung, Aktor, Datensammlung und Anzeige vermischt sind. Globale Variablen, ein Endlosloop auf Modulebene und feste Pfade machen es nicht testbar. Alle folgenden Changes (`fail-safe-shutdown`, `multi-box-decision`, `config-file`, `gpu-required`) brauchen Module mit klaren Schnittstellen, die sich ohne Kamera, GPU und Mikrocontroller prüfen lassen.

## What Changes

- Die Pipeline wird in Module geteilt, die den Capabilities entsprechen: Aufnahme, Erkennung, Relevanzfilter, Entscheidung, Aktor, Datensammlung, Monitoring und Start/Lebenszyklus. Jedes Modul hat eine kleine, austauschbare Schnittstelle.
- Die Entscheidungslogik wird eine reine Funktion mit eingespeister Uhr (keine versteckte `time.time()`-Abhängigkeit), damit sich echte Logs wiedergeben lassen.
- Kamera, serielle Schnittstelle und Modell sind durch Fakes ersetzbar (Testbilder, Pseudo-Terminal, Dummy-Detektor).
- Das Verhalten bleibt gegenüber dem Legacy-System **identisch**, einschließlich der bekannten Mängel. Korrigiert werden sie in den eigenen Changes. So lässt sich der Umbau gegen die Baseline-Specs prüfen.
- Arbeitsteilung: Entwicklung und Tests auf dem Mac. Alles GPU-Lastige (Inferenz-Benchmarks, Training) läuft auf `hba1`. Der Transport des Codes ist als Git mit `git pull` auf `hba1` angenommen und im Design zu bestätigen.

## Capabilities

### New Capabilities
<!-- keine -->

### Modified Capabilities
<!-- keine: reiner Umbau ohne Änderung des beobachtbaren Verhaltens. Die Delta-Specs entfallen, im Spec-Schritt wird `skip_specs: true` gesetzt. -->

## Impact

- **Code:** neues Paket `src/hba/` mit Tests unter `tests/`. `legacy/` bleibt unverändert als Referenz.
- **Abhängigkeiten:** pyserial, OpenCV, ultralytics, pytest. Auf dem Mac läuft alles ohne CUDA.
- **Abhängige Changes:** `fail-safe-shutdown` (Gruppe 4 wartet auf die Hauptschleife), `multi-box-decision`, `config-file`, `gpu-required`.
- **Nicht im Umfang:** Verhaltensänderungen, neue Features, Konfigurationsdatei (`config-file`), Dienst-Einrichtung (`systemd-service`).
