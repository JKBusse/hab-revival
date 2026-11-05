# Design

## Context

Motivation und Umfang stehen in `proposal.md`. Die festen Werte der Baseline liegen nach `modular-pipeline` an einer Stelle pro Modul. Dieser Change verlegt sie in eine geprüfte Konfiguration und liefert ein Werkzeug zum Einstellen von Bildausschnitt und Aktiver Fläche. Verhalten mit Standardwerten bleibt identisch zur Baseline.

## Goals / Non-Goals

**Goals:**
- Ein Start ohne Datei verhält sich wie bisher.
- Fehler in der Datei fallen beim Start auf, nicht im Betrieb.
- Die Kalibrierung ist auf dem Mac ohne GPU nutzbar und zeigt Werte im Maßstab des Filters.

**Non-Goals:**
- Keine automatische Kalibrierung, keine Änderung der Konfiguration im laufenden Betrieb.
- Keine Untergrenze für die Haltezeit (Entscheidung von Jan), nur eine Warnung.

## Decisions

### 1. Frozen Dataclasses plus handgeschriebene Prüfung

`config.py` definiert eine unveränderliche Konfiguration (verschachtelte Dataclasses) mit den Standardwerten der Baseline. `load_config(path, flags)` liest YAML, setzt Werte darüber, wendet Flags an und prüft. Unbekannte Schlüssel werden abgelehnt. Alle Fehler werden gesammelt und gemeinsam gemeldet, damit ein Durchlauf reicht.

*Alternative:* pydantic. Verworfen, weil es auf `hba1` (Python 3.10, feste Pins) eine große zusätzliche Abhängigkeit wäre.

### 2. `ruamel.yaml` statt PyYAML

Das Kalibrier-Werkzeug muss Kommentare und übrige Schlüssel der Datei erhalten. PyYAML verliert Kommentare, `ruamel.yaml` behält sie im Round-Trip. Es ist reines Python und läuft unter 3.10 und 3.13. Das Proposal nennt noch PyYAML und wird angepasst.

### 3. Vorrang: Flag, Datei, Standard

Flags haben `None` als Standard im Parser, damit „nicht übergeben" erkennbar ist. Erst `config.py` füllt Standards. Die Standardwerte der Flags (zum Beispiel `-c 0.4`) stehen dadurch einmal in der Konfiguration, nicht doppelt im Parser.

### 4. Gesamte Prüfung vor dem ersten Frame

Geprüft werden Schlüssel, Typen, Wertebereiche und Querbeziehungen (Ausschnitt innerhalb der Auflösung und der Zeilen bis `hood_rows`, `min_top` und `max_width` innerhalb von 640). Die Haltezeit unter 3 s erzeugt nur eine Warnung. Haltezeit kleiner oder gleich 0 ist ein Fehler, kein Parameter. Fehler enden mit Exit-Code 2 und einer Meldung je Fehler.

### 5. Kalibrierung: GUI dünn, Logik rein

```
 calibrate.py (OpenCV-Fenster, Maus, Tasten)   <- nicht automatisch testbar
        |
        v
 calibration.py (Rechteck-Geometrie, Bildkoordinaten <-> Anzeige,
                 Prüfung, YAML-Schreiben)       <- vollständig testbar
```

Das Werkzeug nutzt dieselben Funktionen für Zuschnitt und Skalierung wie die Pipeline (`capture.py`) und dieselbe Prüfung wie der Start. So kann die Anzeige nicht vom Betrieb abweichen. Die Aktive Fläche wird im 640×640-Bild gezeichnet, weil der Filter dort rechnet.

### 6. Schreiben: atomar und nur geänderte Schlüssel

Das Werkzeug schreibt in eine temporäre Datei im selben Ordner und ersetzt die Zieldatei mit `os.replace`. Es ändert nur die geänderten Schlüssel. Wird die Datei im Betrieb ersetzt, liest der laufende Prozess sie nicht neu (kein Hot-Reload). Wirksam wird sie beim nächsten Start.

### 7. Beispiel-Datei als Referenz

`config/hba.example.yaml` enthält alle Schlüssel mit den Standardwerten und Kommentaren. Ein Test prüft, dass sie geladen die eingebauten Standardwerte ergibt, damit Beispiel und Code nicht auseinanderlaufen.

## Risks / Trade-offs

- **Falscher Wert verschiebt die Aktive Fläche unbemerkt und das System blendet nicht mehr ab** → Der Ausschnitt wird beim Start geloggt (alle effektiven Werte, Quelle je Wert). Das Kalibrier-Werkzeug zeigt vor dem Speichern das Ergebnis. Eine Untergrenze für die Fläche wird bewusst nicht eingebaut.
- **Kurze Haltezeit macht schnelles Aufblenden möglich** → Warnung im Log, sonst Verantwortung beim Betreiber. Das Aufblenden bleibt durch die Firmware und die Freigabe in Reihe nur eine Erlaubnis.
- **OpenCV-Fenster auf `hba1` ohne Display** → Kalibrierung ist für den Mac gedacht. Auf `hba1` reicht das Kopieren der YAML-Datei. Das ist in der README festgehalten.
- **GUI nicht automatisch testbar** → Die Logik liegt in einem eigenen, getesteten Modul. Die GUI bekommt einen Handtest auf dem Mac.

## Migration Plan

1. `config.py`, Beispiel-Datei und Tests schreiben, Pipeline auf die Konfiguration umstellen. Verhalten mit Standardwerten per Golden- und Replay-Tests unverändert.
2. Kalibrier-Werkzeug auf dem Mac entwickeln.
3. Mit einem echten Kamerabild von `hba1` den Standardausschnitt gegenprüfen.

Rollback: Ohne Datei gelten die Standardwerte der Baseline.

## Open Questions

- Gibt es ein Kamerabild von `hba1`, das als Testbild ins Repo darf (Aufnahme aus `images/`)? Sonst nutzt der Handtest ein beliebiges Bild.
