# Spec Delta

## MODIFIED Requirements

### Requirement: Serielle Verbindung
Das System SHALL beim Start `/dev/ttyUSB0` mit 9600 Baud, 8 Datenbits, 1 Stoppbit und 2 Sekunden Timeout öffnen. Das Gerät ist ein CH341-USB-UART-Adapter.

#### Scenario: Adapter vorhanden
- **WHEN** `/dev/ttyUSB0` beim Start verfügbar ist
- **THEN** wird `configure_serial_connection: OK` geloggt
- **AND** der Aktor-Modus ist aktiv

#### Scenario: Adapter fehlt beim Start
- **WHEN** `/dev/ttyUSB0` nicht geöffnet werden kann
- **THEN** wird `configure_serial_connection: ERROR!` geloggt
- **AND** das System läuft weiter und der Status gilt als 0
- **AND** die Wiederverbindung beginnt wie in der Requirement „Wiederverbindung nach Ausfall"

## ADDED Requirements

### Requirement: Heartbeat mit Fail-Safe-Wert
Das System SHALL den Status mindestens alle 0,5 Sekunden an den Mikrocontroller senden. Liegt die letzte Frame-Entscheidung länger als 0,5 Sekunden zurück, SHALL es `0` senden statt des veralteten Status.

#### Scenario: Normalbetrieb
- **WHEN** Frames mit 8 bis 12 Bildern pro Sekunde verarbeitet werden
- **THEN** kommt jeweils der Status des aktuellen Frames beim Mikrocontroller an
- **AND** zwischen zwei Kommandos liegen höchstens 0,5 Sekunden

#### Scenario: Verarbeitung hängt
- **WHEN** der letzte Status `1` war und seit mehr als 0,5 Sekunden keine neue Frame-Entscheidung vorliegt
- **THEN** wird `0\n` gesendet
- **AND** ein altes `1` wird nicht erneut gesendet

### Requirement: Wiederverbindung nach Ausfall
Das System SHALL nach einem Verbindungs- oder Schreibfehler in Abständen von höchstens 5 Sekunden versuchen, die serielle Verbindung neu aufzubauen. Währenddessen SHALL der Status 0 gelten und die Verarbeitung weiterlaufen.

#### Scenario: Adapter wird abgezogen und wieder eingesteckt
- **WHEN** ein Schreibvorgang fehlschlägt und der Adapter später wieder verfügbar ist
- **THEN** wird die Verbindung neu aufgebaut
- **AND** danach werden wieder Kommandos gesendet

#### Scenario: Adapter bleibt weg
- **WHEN** der Adapter dauerhaft fehlt
- **THEN** wird der Verlust einmal als ERROR geloggt
- **AND** mindestens alle 30 Sekunden eine Erinnerung
- **AND** der Status bleibt 0

### Requirement: Abschlusskommando beim Beenden
Das System SHALL beim kontrollierten Beenden vor dem Prozessende `0\n` senden und ausleeren. Das gilt für Strg-C, SIGTERM, die Taste `c` und unbehandelte Exceptions.

#### Scenario: Beenden bei eingeschaltetem Fernlicht
- **WHEN** der letzte Status `1` war und das Programm per Strg-C beendet wird
- **THEN** wird `0\n` gesendet, bevor der Prozess endet

#### Scenario: Beenden per SIGTERM
- **WHEN** ein Dienst-Manager das Programm mit SIGTERM beendet
- **THEN** wird `0\n` gesendet, bevor der Prozess endet

#### Scenario: Adapter beim Beenden nicht verfügbar
- **WHEN** das Programm beendet wird und die serielle Verbindung nicht schreibbar ist
- **THEN** endet der Prozess trotzdem
- **AND** das Beenden dauert wegen des Sendeversuchs höchstens 2 Sekunden länger

## REMOVED Requirements

### Requirement: Dauerhafter Ausfall nach Schreibfehler
**Reason**: Nach dem ersten Schreibfehler lief das System dauerhaft ohne Aktor weiter, ohne es zu bemerken.
**Migration**: Ersetzt durch die Requirement „Wiederverbindung nach Ausfall".

### Requirement: Kein Abschlusskommando beim Beenden (Legacy-Lücke)
**Reason**: Ohne Abschlusskommando blieb ein eingeschaltetes Fernlicht nach dem Programmende an, solange die Firmware nicht selbst abblendete.
**Migration**: Ersetzt durch die Requirement „Abschlusskommando beim Beenden".
