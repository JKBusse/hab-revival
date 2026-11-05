## ADDED Requirements

### Requirement: Autostart beim Boot
Das System SHALL als systemd-Dienst `hba.service` unter dem Benutzer `jkb` beim Boot (`multi-user.target`) starten. Der Dienst hängt weder von einem eingehängten USB-Stick noch von der Netzwerkverbindung ab.

#### Scenario: Rechner startet neu
- **WHEN** `hba1` bootet
- **THEN** startet der Dienst von selbst
- **AND** er wartet nicht auf `/mnt/hba-stick`

### Requirement: Neustart bei Fehler
Das System SHALL den Dienst bei jedem Exit-Code ungleich 0 und bei Absturz nach 10 Sekunden neu starten. Es gibt keine Sperre durch ein Startlimit, damit eine spät erkannte GPU oder ein nachgereichter Mikrocontroller ohne Eingriff zu einem laufenden Dienst führt.

#### Scenario: Keine GPU beim Start
- **WHEN** das Programm mit Exit-Code 3 endet
- **THEN** startet systemd es nach 10 Sekunden erneut
- **AND** das wiederholt sich, bis der Start gelingt

#### Scenario: Watchdog-Abbruch
- **WHEN** das Programm mit Exit-Code 4 endet
- **THEN** startet systemd es nach 10 Sekunden erneut

### Requirement: Gewollter Stopp
Das System SHALL beim Stoppen des Dienstes SIGTERM senden und nach 5 Sekunden hart beenden. Ein Exit-Code 0 löst keinen Neustart aus.

#### Scenario: Dienst stoppen
- **WHEN** `systemctl stop hba` ausgeführt wird
- **THEN** endet das Programm kontrolliert mit Exit-Code 0 und sendet `0\n`
- **AND** systemd startet es nicht neu

#### Scenario: Programm reagiert nicht
- **WHEN** das Programm 5 Sekunden nach SIGTERM noch läuft
- **THEN** beendet systemd es mit SIGKILL

### Requirement: Log im Journal
Das System SHALL die Ausgabe des Programms im Journal (`journalctl -u hba`) bereitstellen. Die Datei-Logs unter dem Ablagepfad bleiben zusätzlich bestehen, wenn die Ablage verfügbar ist.

#### Scenario: Fehlstart ohne Ablage
- **WHEN** das Programm ohne verfügbare Ablage startet
- **THEN** stehen seine Meldungen im Journal

### Requirement: Versionierte Unit-Dateien
Das System SHALL die Unit von `hba.service` und eine Installationsanleitung im Repo unter `deploy/` führen. Die Unit `sensor.service` (Telemetrie) wird dort dokumentiert und von diesem Change nicht verändert.

#### Scenario: Unit im Repo
- **WHEN** jemand `deploy/hba.service` prüft
- **THEN** besteht sie `systemd-analyze verify`
- **AND** enthält `Restart=on-failure`, `RestartSec=10` und `StartLimitIntervalSec=0`
