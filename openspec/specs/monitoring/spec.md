# monitoring Specification

## Purpose
Beschreibt Logging, Live-Anzeige, Bild-Stream und Systemtelemetrie des Legacy-Systems (`yolov8.py`, `stream2.py`, `nvidia1.py`).

## Requirements

### Requirement: Logdatei
Das System SHALL nach `<pfad>/log/<startzeit>.log` mit Stufe DEBUG schreiben. Es SHALL Start, Argumente, Initialisierung, Frame-Beginn und -Ende, Detektionsanzahl, Bewertung, Status und die Frame-Dauer (`DIFF`, Sekunden) loggen.

#### Scenario: Frame-Dauer
- **WHEN** ein Frame abgeschlossen ist
- **THEN** enthält das Log die Zeit seit dem vorherigen Frame

### Requirement: Live-Fenster (`-v`)
Das System SHALL mit `-v` das Bild mit eingezeichneten Boxen in einem OpenCV-Fenster „Result" anzeigen. Die Taste `c` SHALL das Programm beenden.

#### Scenario: Taste c
- **WHEN** das Fenster fokussiert ist und `c` gedrückt wird
- **THEN** wird `Manual end C in CV2` geloggt und das Programm beendet

### Requirement: Boxdarstellung
Das System SHALL Boxen mit 13 Pixeln Abstand zeichnen: gelb, wenn die Box schmaler als 500 Pixel ist, ihre obere Kante aber nicht unter Zeile 160 liegt; rot für Klasse 0 (`back`); weiß für Klasse 1 (`front`). Zu breite Boxen (500 Pixel und mehr) werden nach Klasse gefärbt, nicht gelb (Legacy-Eigenheit). Die Klassennummer steht neben der Box.

#### Scenario: Gegenverkehr im Stream
- **WHEN** eine relevante Box der Klasse 1 gezeichnet wird
- **THEN** ist sie weiß

#### Scenario: Box zu weit oben
- **WHEN** eine Box schmaler als 500 Pixel ist und ihre obere Kante bei y=100 liegt
- **THEN** ist sie gelb

#### Scenario: Zu breite Box
- **WHEN** eine Box 560 Pixel breit ist und zur Klasse 1 gehört
- **THEN** ist sie weiß und nicht gelb

### Requirement: Bild-Stream (`-S`)
Das System SHALL mit `-S` in jedem Frame das annotierte Bild als PNG nach `/tmp/<zeitstempel>.png` schreiben. Der Flask-Dienst `stream2.py` SHALL auf `0.0.0.0:5000` unter `/stream` das jeweils neueste Bild aus `/tmp` als Multipart-Stream ausliefern (alle 0,3 s) und alle `.png`, `.jpg` und `.jpeg` in `/tmp` außer den neuesten 10 löschen.

#### Scenario: Stream abrufen
- **WHEN** ein Client `http://<host>:5000/stream` aufruft
- **THEN** erhält er laufend das neueste Bild

#### Scenario: Aufräumen
- **WHEN** mehr als 10 Bilddateien in `/tmp` liegen
- **THEN** werden alle älteren gelöscht, auch fremde Dateien

### Requirement: Keine Zugriffskontrolle auf den Stream
Der Stream-Dienst SHALL ohne Authentifizierung und mit Flask-Debug-Modus auf allen Netzwerkschnittstellen laufen. Dieses Verhalten ist ein bekanntes Risiko.

#### Scenario: Zugriff aus dem Netz
- **WHEN** ein beliebiger Rechner im Netz Port 5000 erreicht
- **THEN** wird das Bild ohne Anmeldung geliefert

### Requirement: Systemtelemetrie per MQTT
Das System SHALL über `nvidia1.py` jede Sekunde Messwerte per `mosquitto_pub` an den Broker `knusperhaus.ddns.net` senden. Themen unter `/home/data/hba/cpu/` sind `temperature`, `memory_used`, `swap_used`, `load`. Themen unter `/home/data/hba/gpu/` sind `power`, `auslastung`, `temperature`, `fan`, `memory_used`. Der Dienst läuft auf `hba1` beim Boot automatisch. Der Mechanismus dafür ist nicht dokumentiert.

#### Scenario: Normaler Betrieb
- **WHEN** der Dienst läuft
- **THEN** erscheint jede Sekunde ein Satz Messwerte auf den genannten Themen

#### Scenario: GPU nicht verfügbar
- **WHEN** die GPU vom Bus fällt
- **THEN** schlägt die Abfrage fehl und der Dienst liefert keine GPU-Werte mehr

### Requirement: Sauberes Beenden
Das System SHALL bei Strg-C `Manual end CTR-C` und `---END---` loggen, Fenster schließen und mit Exit-Code 0 beenden.

#### Scenario: Strg-C
- **WHEN** SIGINT eintrifft
- **THEN** wird `---END---` geloggt und das Programm beendet
