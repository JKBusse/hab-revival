# object-detection Specification

## Purpose
Beschreibt die Fahrzeugerkennung per YOLOv8 im Legacy-System: Modell, Klassen, Schwellen und Rechengerät.

## Requirements

### Requirement: Modell wird beim Start geladen
Das System SHALL das YOLOv8-Modell einmal beim Start laden. Der Standardpfad ist `/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt` und über `-m` änderbar.

#### Scenario: Eigenes Modell angegeben
- **WHEN** `-m /pfad/zum/modell.pt` übergeben wird
- **THEN** wird dieses Modell statt des Standardmodells geladen

#### Scenario: Modell nicht ladbar
- **WHEN** das Modell nicht geladen werden kann
- **THEN** wird die Exception geloggt und das Programm beendet

### Requirement: Zwei Klassen
Das System SHALL die Klassen `back` (Index 0, Fahrzeug von hinten, Rücklichter) und `front` (Index 1, Fahrzeug von vorne, Scheinwerfer) unterscheiden. Die Reihenfolge entspricht `names: ['back', 'front']` im Dataset.

#### Scenario: Gegenverkehr
- **WHEN** ein Fahrzeug von vorne erkannt wird
- **THEN** meldet das Modell Klasse 1

#### Scenario: Vorausfahrendes Fahrzeug
- **WHEN** ein Fahrzeug von hinten erkannt wird
- **THEN** meldet das Modell Klasse 0

### Requirement: Konfidenzschwelle
Das System SHALL nur Detektionen mit einer Konfidenz ab dem Schwellwert berücksichtigen. Der Standardwert ist 0,4, änderbar über `-c`.

#### Scenario: Detektion unter der Schwelle
- **WHEN** das Modell eine Detektion mit Konfidenz 0,3 liefert und die Schwelle 0,4 beträgt
- **THEN** wird sie verworfen

### Requirement: Rechengerät
Das System SHALL das Rechengerät über `-d` wählen. Der Standardwert ist `cpu`. Ein Wechsel auf die GPU (`-d 0` oder `cuda`) muss explizit erfolgen.

#### Scenario: Kein Flag
- **WHEN** `-d` nicht angegeben wird
- **THEN** läuft die Inferenz auf der CPU

### Requirement: Inferenz pro Frame
Das System SHALL jeden erfassten Frame (640×640) genau einmal durch das Modell schicken und Boxen (Koordinaten xyxy im 640×640-Raum), Klassen und Konfidenzen auswerten.

#### Scenario: Frame ohne Treffer
- **WHEN** das Modell keine Box liefert
- **THEN** wird `No Detect` ausgegeben
- **AND** die Entscheidungslogik läuft trotzdem weiter
