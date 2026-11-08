## MODIFIED Requirements

### Requirement: Flags für die Erkennung
Das System SHALL die Flags `-c`/`--conf` (Konfidenzschwelle, Standard 0.4), `-d`/`--device` (Standard `0`, erste GPU) und `-m`/`--model` (Standard `/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt`) unterstützen.

#### Scenario: GPU wählen
- **WHEN** `-d 0` übergeben wird
- **THEN** läuft die Inferenz auf der ersten GPU

#### Scenario: CPU wählen
- **WHEN** `-d cpu` übergeben wird
- **THEN** läuft die Inferenz auf der CPU

## ADDED Requirements

### Requirement: Exit-Codes
Das System SHALL mit festen Exit-Codes enden: 0 gewollter Stopp, 1 Laufzeitfehler (auch CUDA-Fehler), 2 ungültige Konfiguration, 3 keine nutzbare GPU beim Start, 4 Watchdog (hängende Hauptschleife). Jeder Code ungleich 0 SHALL im Log mit seinem Grund stehen.

#### Scenario: Keine GPU
- **WHEN** das Programm wegen fehlender GPU endet
- **THEN** ist der Exit-Code 3
- **AND** das Log nennt den Grund

#### Scenario: Gewollter Stopp
- **WHEN** das Programm per SIGTERM endet
- **THEN** ist der Exit-Code 0
