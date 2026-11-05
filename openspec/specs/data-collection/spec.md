# data-collection Specification

## Purpose
Beschreibt, wie das Legacy-System im laufenden Betrieb Bilder und automatisch erzeugte Labels für späteres Training sammelt.

## Requirements

### Requirement: Dateinamen
Das System SHALL gespeicherte Dateien nach dem Zeitstempel des Frames benennen (`time.time()` ohne Punkt, zum Beispiel `16983655482767072.png`).

#### Scenario: Frame wird gespeichert
- **WHEN** ein Bild gespeichert wird
- **THEN** besteht der Dateiname aus dem Zeitstempel ohne Punkt und der Endung `.png`

### Requirement: Alle Ausschnitte speichern (`-s`)
Das System SHALL mit dem Flag `-s` jeden Erkennungsausschnitt (960×426, vor der Skalierung) als PNG nach `<pfad>/images/crop/` schreiben. Für diesen Ordner gibt es keine Mengenbegrenzung.

#### Scenario: Flag gesetzt
- **WHEN** `-s` aktiv ist
- **THEN** wird in jedem Frame ein Ausschnitt gespeichert

#### Scenario: Flag nicht gesetzt
- **WHEN** `-s` nicht aktiv ist
- **THEN** werden keine Ausschnitte in `images/crop/` gespeichert

### Requirement: Zufällige Stichproben
Das System SHALL unabhängig vom Flag `-s` mit einer Wahrscheinlichkeit von etwa 1 % pro Frame (`randrange(1, 100) == 42`) den Ausschnitt nach `<pfad>/images/random/` speichern und diesen Ordner auf höchstens 1000 Dateien begrenzen. Die ältesten Dateien werden zuerst gelöscht.

#### Scenario: Ordner läuft über
- **WHEN** `images/random/` mehr als 1000 Dateien enthält
- **THEN** werden die ältesten gelöscht, bis 1000 übrig sind

### Requirement: Detektionsbeispiele mit Auto-Label
Das System SHALL unabhängig vom Flag `-s` in Frames mit mindestens einer Detektion mit einer Wahrscheinlichkeit von etwa 9 % (`randrange(1, 100) > 90`) das skalierte 640×640-Bild ohne eingezeichnete Boxen nach `<pfad>/images/detections/` und eine YOLO-Labeldatei nach `<pfad>/labels/detections/` schreiben. Beide Ordner SHALL auf höchstens 1000 Dateien begrenzt werden.

#### Scenario: Detektion mit Speicherung
- **WHEN** ein Frame eine Detektion enthält und der Zufallswert über 90 liegt
- **THEN** werden Bild und Label mit demselben Zeitstempel gespeichert

### Requirement: Label-Format
Das System SHALL Labels im YOLO-Format schreiben: `<klasse> <x_center> <y_center> <breite> <höhe>`, jeweils normiert durch 640. Es wird nur die **erste** Box des Frames geschrieben.

#### Scenario: Frame mit zwei Boxen
- **WHEN** ein Frame zwei Detektionen enthält
- **THEN** enthält die Labeldatei nur eine Zeile für die erste Box
- **AND** das gespeicherte Bild zeigt beide Fahrzeuge

### Requirement: Vorbereiteter Speicherort
Das System SHALL voraussetzen, dass die Ordner `log/`, `labels/detections/`, `images/crop/`, `images/random/` und `images/detections/` unter dem Pfad (Standard `/mnt/hba-stick/HBA/`) bereits existieren. Es legt sie nicht an.

#### Scenario: Ordner fehlen
- **WHEN** ein benötigter Ordner nicht existiert
- **THEN** schlägt der Start oder der erste Schreibvorgang mit einer Exception fehl
