## MODIFIED Requirements

### Requirement: Abgeblendet beim Start
Das System SHALL den Zeitpunkt der letzten relevanten Detektion beim Start auf die Startzeit setzen. Dadurch bleibt das Fernlicht nach dem Start für die Dauer der Haltezeit abgeblendet.

#### Scenario: Start ohne Fahrzeug
- **WHEN** das System startet und keine Detektion auftritt
- **THEN** ist der Status 0, bis die Haltezeit seit dem Start vergangen ist
- **AND** danach 1

### Requirement: Verzögertes Aufblenden
Das System SHALL den Status erst auf 1 setzen, wenn seit der letzten relevanten Detektion mindestens die konfigurierte Haltezeit vergangen ist (Standard 3 Sekunden, Sekundenauflösung). Abblenden erfolgt unabhängig davon sofort. Die Richtung ist nicht konfigurierbar.

#### Scenario: Fahrzeug verschwindet
- **WHEN** die Haltezeit 3 Sekunden beträgt und zuletzt vor 2 Sekunden eine relevante Detektion auftrat
- **THEN** bleibt der Status 0

#### Scenario: Freie Sicht
- **WHEN** seit mindestens der Haltezeit keine relevante Detektion auftrat
- **THEN** ist der Status 1

#### Scenario: Einzelner verpasster Frame
- **WHEN** ein Fahrzeug in einem Frame nicht erkannt wird, aber innerhalb der Haltezeit erkannt wurde
- **THEN** bleibt der Status 0

#### Scenario: Längere Haltezeit
- **WHEN** die Haltezeit 5 Sekunden beträgt und zuletzt vor 4 Sekunden eine relevante Detektion auftrat
- **THEN** bleibt der Status 0
