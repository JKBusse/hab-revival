## MODIFIED Requirements

### Requirement: Rechengerät
Das System SHALL das Rechengerät über `-d` wählen. Der Standardwert ist die erste GPU (`0`). Die CPU (`-d cpu`) ist nur auf ausdrückliche Anforderung möglich und SHALL beim Start eine Warnung auslösen, dass sie für den Betrieb nicht vorgesehen ist.

#### Scenario: Kein Flag
- **WHEN** `-d` nicht angegeben wird
- **THEN** läuft die Inferenz auf der ersten GPU

#### Scenario: CPU ausdrücklich gewählt
- **WHEN** `-d cpu` übergeben wird
- **THEN** läuft die Inferenz auf der CPU
- **AND** ein WARNING nennt, dass dies nur für Entwicklung und Tests gedacht ist

## ADDED Requirements

### Requirement: Start-Prüfung der GPU
Das System SHALL beim Start mit einer GPU als Gerät prüfen, dass CUDA verfügbar ist, das Modell auf die GPU geladen werden kann und ein Warm-up-Frame innerhalb von 30 Sekunden verarbeitet wird. Erst danach beginnt die Hauptschleife und der Status 1 darf gesendet werden. Schlägt ein Schritt fehl, SHALL das System einen ERROR loggen, `0` senden und mit Exit-Code 3 enden. Es gibt keinen CPU-Fallback.

#### Scenario: Keine GPU vorhanden
- **WHEN** das System mit GPU als Gerät startet und CUDA nicht verfügbar ist
- **THEN** wird ein ERROR geloggt
- **AND** `0\n` wird an den Aktor gesendet
- **AND** der Prozess endet mit Exit-Code 3

#### Scenario: Warm-up hängt
- **WHEN** der Warm-up-Frame nach 30 Sekunden nicht fertig ist
- **THEN** endet der Prozess mit Exit-Code 3

#### Scenario: GPU in Ordnung
- **WHEN** CUDA verfügbar ist und der Warm-up gelingt
- **THEN** beginnt die Hauptschleife

### Requirement: GPU-Fehler im Betrieb
Das System SHALL bei einem CUDA-Fehler während der Inferenz keine Neuinitialisierung im selben Prozess versuchen, sondern `0` senden und mit Exit-Code 1 enden. Der Neustart obliegt dem Dienst-Manager.

#### Scenario: CUDA-Fehler
- **WHEN** die Inferenz einen CUDA-Fehler wirft
- **THEN** wird `0\n` an den Aktor gesendet
- **AND** der Prozess endet mit Exit-Code 1

### Requirement: Watchdog für die Hauptschleife
Das System SHALL die Hauptschleife in einem eigenen Thread überwachen. Wurde länger als 5 Sekunden kein Frame fertig verarbeitet, SHALL der Watchdog `0` senden (soweit möglich), einen ERROR loggen und den Prozess hart mit Exit-Code 4 beenden, ohne auf die Hauptschleife zu warten.

#### Scenario: Hängende Inferenz
- **WHEN** die Inferenz nicht mehr zurückkehrt
- **THEN** beendet der Watchdog den Prozess nach höchstens 6 Sekunden (5 Sekunden Schwelle plus Prüfintervall von 1 Sekunde) mit Exit-Code 4, und der Aktor erhält spätestens nach etwa 1 Sekunde `0`

#### Scenario: Normale Frame-Dauer
- **WHEN** Frames in 0,1 bis 0,2 Sekunden verarbeitet werden
- **THEN** greift der Watchdog nicht ein
