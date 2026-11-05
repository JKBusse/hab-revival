# Proposal

## Why

Wichtige Werte stehen fest im Quelltext: Bildausschnitt (Zeilen 0–850 und 212–638, Spalten 400–1360), Aktive Fläche (Breite < 500, obere Kante > 160), Haltezeit 3 s, Serial-Port, Baudrate, Stichproben-Wahrscheinlichkeiten und Dateilimit. Wer die Kamera anders montiert oder das System in einem anderen Fahrzeug einsetzt, muss den Quelltext ändern. Die Werte sind außerdem undokumentiert und ohne Prüfung.

## What Changes

- Alle bisher festen Werte kommen in eine **YAML-Konfigurationsdatei** mit den Legacy-Werten als Standard. Die bisherigen Kommandozeilen-Flags bleiben für Einzelwerte erhalten.
- Die Datei wird beim Start **geprüft**. Ungültige oder gefährliche Werte brechen den Start mit klarer Meldung ab. Eine Haltezeit unter 3 s erzeugt nur eine **Warnung**, es gibt bewusst keine Untergrenze (Entscheidung von Jan). Die Richtung (Abblenden sofort, Aufblenden verzögert) bleibt unveränderlich.
- Neu: eine **Kalibrier-Hilfe**. Sie zeigt in einem OpenCV-Fenster auf einem Kamerabild den Bildausschnitt und die Aktive Fläche, lässt sie per Maus verändern und schreibt die Werte in die Konfiguration. Sie läuft ohne GPU (auf dem Mac mit einem Testbild oder auf `hba1`).

## Capabilities

### New Capabilities
- `camera-calibration`: Anzeigen und Einstellen von Bildausschnitt und Aktiver Fläche auf einem Kamerabild, Schreiben in die Konfiguration.

### Modified Capabilities
- `runtime-configuration`: Konfigurationsdatei mit Prüfung beim Start ersetzt die Anforderung „Feste Werte im Code".
- `image-capture`: Bildausschnitt, Skalierung, Drehung und Auflösung sind konfigurierbar.
- `relevance-filter`: Schwellen der Aktiven Fläche sind konfigurierbar.
- `high-beam-decision`: Haltezeit ist konfigurierbar, ohne Untergrenze (nur Warnung). Die Richtung (Abblenden sofort, Aufblenden verzögert) bleibt unveränderlich.

## Impact

- **Code:** Konfigurationsmodul im neuen Paket, Kalibrier-Werkzeug als eigener Einstiegspunkt.
- **Abhängigkeiten:** `ruamel.yaml` (erhält Kommentare beim Schreiben).
- **Betrieb:** Eine Beispiel-Konfiguration mit den Legacy-Werten wird mitgeliefert, damit ein Start ohne eigene Datei dasselbe Verhalten zeigt wie bisher.
- **Voraussetzung:** `modular-pipeline`.
- **Nicht im Umfang:** Automatische Kalibrierung per Bilderkennung, Konfigurationsänderung im laufenden Betrieb.
