# runtime-configuration Specification

## Purpose
Beschreibt, wie das Legacy-System konfiguriert und gestartet wird: Kommandozeilen-Flags, Standardwerte, Fehlerverhalten und fehlender Autostart.

## Requirements

### Requirement: Flags für Ausgabe und Datensammlung
Das System SHALL die Flags `-v`/`--video` (Live-Fenster), `-S`/`--stream` (Bild-Stream nach `/tmp`) und `-s`/`--save` (Ausschnitte speichern) unterstützen. Alle drei sind standardmäßig aus.

#### Scenario: Start ohne Flags
- **WHEN** das Programm ohne Argumente startet
- **THEN** gibt es kein Fenster, keinen Stream und keine gespeicherten Ausschnitte

### Requirement: Flags für die Erkennung
Das System SHALL die Flags `-c`/`--conf` (Konfidenzschwelle, Standard 0.4), `-d`/`--device` (Standard `0`, erste GPU) und `-m`/`--model` (Standard `/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt`) unterstützen.

#### Scenario: GPU wählen
- **WHEN** `-d 0` übergeben wird
- **THEN** läuft die Inferenz auf der ersten GPU

#### Scenario: CPU wählen
- **WHEN** `-d cpu` übergeben wird
- **THEN** läuft die Inferenz auf der CPU

### Requirement: Flags für die Kamera
Das System SHALL die Flags `-e`/`--exposure` (1 manuell, 3 automatisch, Standard 1), `-t`/`--time` (Belichtungszeit 0–5000, Standard 700) und `-b`/`--brightness` (−180 bis 180, Standard nicht gesetzt) unterstützen.

#### Scenario: Belichtungszeit ändern
- **WHEN** `-t 1200` übergeben wird
- **THEN** wird die absolute Belichtungszeit auf 1200 gesetzt

### Requirement: Flag für den Speicherort
Das System SHALL über `-p`/`--path` den Basispfad für Logs, Bilder und Labels festlegen. Der Standard ist `/mnt/hba-stick/HBA/`.

#### Scenario: Anderer Speicherort
- **WHEN** `-p /data/hba/` übergeben wird
- **THEN** liegen Logs, Bilder und Labels unter `/data/hba/`

### Requirement: Feste Werte im Code
Das System SHALL folgende Werte fest im Quelltext tragen, ohne Konfiguration von außen: Video-Device 0, Auflösung 1920×1080, Bildausschnitt, Aktive Fläche (500 / 160), Haltezeit 3 s, Serial-Port und Baudrate, Stichproben-Wahrscheinlichkeiten, Dateilimit 1000.

#### Scenario: Haltezeit ändern
- **WHEN** jemand die Haltezeit von 3 s ändern will
- **THEN** muss er den Quelltext bearbeiten

### Requirement: Unbehandelte Fehler beenden das Programm
Das System SHALL unbehandelte Exceptions loggen und das Programm mit Exit-Code 0 beenden. Ein Neustart erfolgt nicht automatisch.

#### Scenario: Unerwarteter Fehler
- **WHEN** eine Exception nicht abgefangen wird
- **THEN** wird `Unhandled exception` geloggt und `---END---` ausgegeben
- **AND** der Prozess endet

### Requirement: Kein dokumentierter Autostart
Das System SHALL im Repo keine Service-Definition, keinen Autostart und keine Konfigurationsdatei mitbringen. Der Start des Hauptprogramms im Fahrzeug erfolgt manuell oder über einen nicht dokumentierten Mechanismus.

#### Scenario: Neustart des Rechners
- **WHEN** `hba1` neu startet
- **THEN** startet das Fernlicht-Programm nicht nachweislich von selbst

### Requirement: Exit-Codes
Das System SHALL mit festen Exit-Codes enden: 0 gewollter Stopp, 1 Laufzeitfehler (auch CUDA-Fehler), 2 ungültige Konfiguration, 3 keine nutzbare GPU beim Start, 4 Watchdog (hängende Hauptschleife). Jeder Code ungleich 0 SHALL im Log mit seinem Grund stehen.

#### Scenario: Keine GPU
- **WHEN** das Programm wegen fehlender GPU endet
- **THEN** ist der Exit-Code 3
- **AND** das Log nennt den Grund

#### Scenario: Gewollter Stopp
- **WHEN** das Programm per SIGTERM endet
- **THEN** ist der Exit-Code 0
