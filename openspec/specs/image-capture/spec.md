# image-capture Specification

## Purpose
Beschreibt, wie das Legacy-System (`legacy/yolov8.py`) Kamerabilder erfasst und für die Objekterkennung vorbereitet: Kameraformat, Belichtung, Ausrichtung und Bildausschnitt.

## Requirements

### Requirement: Kameraquelle und Format
Das System SHALL das erste Video-Device (`/dev/video0`) über OpenCV öffnen, das Pixelformat MJPG anfordern und eine Auflösung von 1920×1080 setzen.

#### Scenario: Normaler Start
- **WHEN** das System startet und die Kamera erreichbar ist
- **THEN** werden MJPG und 1920×1080 gesetzt
- **AND** die tatsächlich gemeldete Breite wird ausgegeben

### Requirement: Manuelle Belichtung als Standard
Das System SHALL die Kamera über `v4l2-ctl` auf feste Belichtung stellen: Netzfrequenz-Filter 50 Hz, Auto-Belichtung aus (Modus 1), absolute Belichtungszeit 700 (per `-t` änderbar), dynamische Framerate aus.

#### Scenario: Standardparameter
- **WHEN** keine Belichtungs-Flags übergeben werden
- **THEN** gilt Modus 1 mit Belichtungszeit 700

#### Scenario: Helligkeit vorgegeben
- **WHEN** `-b <Wert>` übergeben wird
- **THEN** wird die Auto-Belichtung (Modus 3) aktiviert
- **AND** die Helligkeit auf den Wert gesetzt

### Requirement: Kamera-Initialisierung ist nicht zwingend
Das System SHALL einen fehlgeschlagenen Kamera-Setup-Schritt nur loggen und trotzdem weiterlaufen. (Legacy-Verhalten, kein Abbruch.)

#### Scenario: Netzfrequenz-Befehl schlägt fehl
- **WHEN** der `v4l2-ctl`-Befehl für die Netzfrequenz einen Fehlercode liefert
- **THEN** wird `initialize_camera: ERROR!` geloggt
- **AND** die übrigen Belichtungs- und Auflösungseinstellungen werden nicht angewendet
- **AND** das System läuft weiter

### Requirement: Bildausrichtung
Das System SHALL jedes Bild um 180° drehen, weil die Kamera kopfüber montiert ist.

#### Scenario: Frame erfasst
- **WHEN** ein Frame gelesen wurde
- **THEN** wird er um 180° gedreht, bevor er weiterverarbeitet wird

### Requirement: Bildausschnitt für die Erkennung
Das System SHALL aus dem gedrehten Bild die Motorhauben-Spiegelung entfernen (Zeilen 0–850) und daraus den Erkennungsausschnitt (Zeilen 212–638, Spalten 400–1360, also 960×426 Pixel) wählen. Der Ausschnitt SHALL mit INTER_AREA auf 640×640 skaliert werden, bevor er das Modell erreicht. Die Seitenverhältnisse werden dabei nicht erhalten.

#### Scenario: Ausschnitt und Skalierung
- **WHEN** ein gedrehter 1920×1080-Frame vorliegt
- **THEN** entsteht ein 960×426-Ausschnitt
- **AND** daraus ein 640×640-Eingabebild für die Erkennung

### Requirement: Fehlgeschlagenes Lesen beendet das Programm
Wenn `camera.read()` kein Bild liefert, SHALL das Programm über den globalen Exception-Handler loggen und beenden. Das Ergebnis des Lesens wird im Legacy-Code nicht geprüft.

#### Scenario: Kamera liefert kein Bild
- **WHEN** `camera.read()` kein gültiges Bild liefert und die Weiterverarbeitung eine Exception auslöst
- **THEN** wird `Unhandled exception` geloggt
- **AND** das Programm beendet sich mit Exit-Code 0
