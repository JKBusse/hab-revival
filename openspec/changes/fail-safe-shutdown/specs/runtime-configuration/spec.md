# Spec Delta

## MODIFIED Requirements

### Requirement: Unbehandelte Fehler beenden das Programm
Das System SHALL unbehandelte Exceptions loggen, den Aktor abblenden und das Programm mit einem Exit-Code ungleich 0 beenden. Ein Neustart erfolgt nicht automatisch.

#### Scenario: Unerwarteter Fehler
- **WHEN** eine Exception nicht abgefangen wird
- **THEN** wird `Unhandled exception` geloggt und `---END---` ausgegeben
- **AND** `0\n` wird an den Aktor gesendet (siehe Spec `actuator-control`)
- **AND** der Prozess endet mit einem Exit-Code ungleich 0

## ADDED Requirements

### Requirement: Beenden per Signal
Das System SHALL die Signale SIGINT und SIGTERM abfangen und kontrolliert beenden: loggen, Aktor abblenden, Fenster schließen. Der Exit-Code ist 0.

#### Scenario: SIGTERM von einem Dienst-Manager
- **WHEN** das Programm SIGTERM erhält
- **THEN** wird `---END---` geloggt
- **AND** `0\n` wird an den Aktor gesendet
- **AND** der Prozess endet mit Exit-Code 0

#### Scenario: SIGKILL
- **WHEN** das Programm mit SIGKILL beendet wird
- **THEN** kann es kein Abschlusskommando senden
- **AND** das Abblenden übernimmt der Firmware-Timeout von 1 bis 3 Sekunden
