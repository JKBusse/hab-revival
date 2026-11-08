# high-beam-decision Specification

## Purpose
Beschreibt die Entscheidungslogik, die aus den Detektionen den Fernlichtzustand ableitet. Sicherheitsrelevant: Abblenden erfolgt sofort, Aufblenden nur nach durchgehend freier Sicht, damit verpasste Frames (False Negatives) Gegenverkehr nicht blenden.

## Requirements

### Requirement: Zustandswerte
Das System SHALL pro Frame einen Status `hbaStatus` bestimmen: `1` bedeutet Fernlicht erlaubt (AN), `0` bedeutet abgeblendet (AUS).

#### Scenario: Status je Frame
- **WHEN** ein Frame vollständig verarbeitet wurde
- **THEN** liegt ein Status 0 oder 1 vor und wird geloggt (`HBA Status: 0|1`)

### Requirement: Abgeblendet beim Start
Das System SHALL den Zeitpunkt der letzten relevanten Detektion beim Start auf die Startzeit setzen. Dadurch bleibt das Fernlicht in den ersten 3 Sekunden nach dem Start abgeblendet.

#### Scenario: Start ohne Fahrzeug
- **WHEN** das System startet und keine Detektion auftritt
- **THEN** ist der Status 0, bis 3 Sekunden seit dem Start vergangen sind
- **AND** danach 1

### Requirement: Sofortiges Abblenden
Das System SHALL den Status in dem Frame auf 0 setzen, in dem eine relevante Detektion den Zeitpunkt der letzten Detektion aktualisiert.

#### Scenario: Gegenverkehr erscheint
- **WHEN** der Status 1 ist und ein Frame eine relevante Detektion mit ausreichender Konfidenz enthält
- **THEN** ist der Status im selben Frame 0

### Requirement: Verzögertes Aufblenden
Das System SHALL den Status erst dann auf 1 setzen, wenn seit der letzten relevanten Detektion mindestens 3 Sekunden vergangen sind (`lastDetectTimer + 3 <= jetzt`, Sekundenauflösung).

#### Scenario: Fahrzeug verschwindet
- **WHEN** zuletzt vor 2 Sekunden eine relevante Detektion auftrat
- **THEN** bleibt der Status 0

#### Scenario: Freie Sicht
- **WHEN** seit mindestens 3 Sekunden keine relevante Detektion auftrat
- **THEN** ist der Status 1

#### Scenario: Einzelner verpasster Frame
- **WHEN** ein Fahrzeug in einem Frame nicht erkannt wird, aber innerhalb der letzten 3 Sekunden erkannt wurde
- **THEN** bleibt der Status 0

### Requirement: Aktualisierung höchstens einmal pro Sekunde
Das System SHALL den Zeitpunkt der letzten Detektion höchstens einmal pro ganzer Sekunde aktualisieren (Drosselung über `lastDetectTimer1`, Sekundenauflösung).

#### Scenario: Dauerhafte Detektion
- **WHEN** über mehrere Sekunden in jedem Frame ein Fahrzeug erkannt wird
- **THEN** wird der Zeitpunkt etwa einmal pro Sekunde aktualisiert
- **AND** der Status bleibt 0

### Requirement: Alle Boxen werden bewertet
Das System SHALL für die Entscheidung jede Box eines Frames einzeln auf Relevanz prüfen (Breite, obere Kante, Konfidenz). Der Zeitpunkt der letzten Detektion wird aktualisiert, sobald mindestens eine Box relevant ist, unabhängig von ihrer Position in der Boxliste.

#### Scenario: Zweites Fahrzeug relevant, erstes nicht
- **WHEN** ein Frame zwei Boxen enthält und nur die zweite die Aktive Fläche erfüllt
- **THEN** wird der Zeitpunkt der letzten Detektion aktualisiert
- **AND** der Status ist im selben Frame 0

#### Scenario: Erstes Fahrzeug relevant, zweites nicht
- **WHEN** ein Frame zwei Boxen enthält und nur die erste die Aktive Fläche erfüllt
- **THEN** wird der Zeitpunkt der letzten Detektion aktualisiert

#### Scenario: Keine Box relevant
- **WHEN** ein Frame Boxen enthält, aber keine die Aktive Fläche erfüllt
- **THEN** wird der Zeitpunkt der letzten Detektion nicht aktualisiert

### Requirement: Nie weniger Abblenden als vorher
Das System SHALL für jede Frame-Folge in jedem Frame einen Status liefern, der nicht größer ist als der Status der bisherigen Logik (nur erste Box) für dieselbe Folge.

#### Scenario: Wiedergabe echter Fahrt-Logs
- **WHEN** die aufgezeichneten Frames der echten Fahrt-Logs mit der neuen Logik wiedergegeben werden
- **THEN** ist der Status in keinem Frame 1, wo die bisherige Logik 0 lieferte

#### Scenario: Zufällige Frame-Folgen
- **WHEN** beliebige Folgen von Frames mit beliebigen Boxen und Zeitpunkten mit beiden Logiken ausgewertet werden
- **THEN** ist der Status der neuen Logik nie größer als der der bisherigen
