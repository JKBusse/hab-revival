# actuator-control Specification

## Purpose
Beschreibt, wie das Legacy-System den Fernlichtzustand per Serial an den Mikrocontroller meldet, der das Fernlicht-Relais schaltet. Die Firmware des Mikrocontrollers ist nicht Teil dieses Repos.

## Requirements

### Requirement: Serielle Verbindung
Das System SHALL beim Start `/dev/ttyUSB0` mit 9600 Baud, 8 Datenbits, 1 Stoppbit und 2 Sekunden Timeout öffnen. Das Gerät ist ein CH341-USB-UART-Adapter.

#### Scenario: Adapter vorhanden
- **WHEN** `/dev/ttyUSB0` beim Start verfügbar ist
- **THEN** wird `configure_serial_connection: OK` geloggt
- **AND** der Aktor-Modus ist aktiv

#### Scenario: Adapter fehlt beim Start
- **WHEN** `/dev/ttyUSB0` nicht geöffnet werden kann
- **THEN** wird `configure_serial_connection: ERROR!` geloggt
- **AND** das System läuft ohne Aktor weiter

### Requirement: Kommandoprotokoll
Das System SHALL den Status in jedem Frame als ASCII-Zeile an den Mikrocontroller senden: `1\n` bedeutet Fernlicht erlaubt, `0\n` bedeutet abgeblendet.

#### Scenario: Freie Sicht
- **WHEN** der Status 1 ist
- **THEN** wird `1\n` gesendet

#### Scenario: Abblenden
- **WHEN** der Status 0 ist
- **THEN** wird `0\n` gesendet

### Requirement: Dauerhafter Ausfall nach Schreibfehler
Das System SHALL nach einem Schreibfehler den Aktor-Modus dauerhaft abschalten und `Serial not Possible!` ausgeben. Es gibt keinen Wiederverbindungsversuch.

#### Scenario: Adapter wird abgezogen
- **WHEN** ein Schreibvorgang eine Exception auslöst
- **THEN** werden keine weiteren Kommandos mehr gesendet
- **AND** das System läuft weiter

### Requirement: Kein Abschlusskommando beim Beenden (Legacy-Lücke)
Das System SHALL beim Beenden (Strg-C, Taste `c`, unbehandelte Exception) kein abschließendes Kommando senden. Der zuletzt gesendete Zustand bleibt am Mikrocontroller bestehen. Ob die Firmware bei ausbleibenden Kommandos abblendet, ist unbekannt. Dieses Verhalten ist ein bekannter Sicherheitsmangel und wird in einem Change korrigiert.

#### Scenario: Programm stürzt bei Status 1 ab
- **WHEN** der zuletzt gesendete Status 1 war und das Programm beendet wird
- **THEN** wird kein `0\n` gesendet
- **AND** das Fernlicht kann eingeschaltet bleiben
