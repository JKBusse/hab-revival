## ADDED Requirements

### Requirement: Konfigurationsdatei
Das System SHALL eine YAML-Konfigurationsdatei lesen. Der Pfad kommt aus `--config <pfad>`, sonst aus `./hba.yaml`, sonst gelten nur die eingebauten Standardwerte. Diese Standardwerte entsprechen dem bisherigen Verhalten.

#### Scenario: Start ohne Datei
- **WHEN** weder `--config` noch `./hba.yaml` vorhanden sind
- **THEN** läuft das System mit den bisherigen Werten

#### Scenario: Angegebene Datei fehlt
- **WHEN** `--config <pfad>` auf eine nicht vorhandene Datei zeigt
- **THEN** bricht der Start mit klarer Meldung und Exit-Code ungleich 0 ab

### Requirement: Konfigurierbare Werte
Das System SHALL diese Werte aus der Datei beziehen: Video-Device, Auflösung, Drehung, Bildausschnitt, Aktive Fläche, Haltezeit, Serial-Port, Baudrate, Stichproben-Wahrscheinlichkeiten und Dateilimit sowie die Werte der Flags `-c`, `-d`, `-m`, `-p`, `-e`, `-t`, `-b`.

#### Scenario: Serial-Port geändert
- **WHEN** die Datei einen anderen Serial-Port nennt
- **THEN** öffnet das System diesen Port

### Requirement: Vorrang der Quellen
Das System SHALL Werte in dieser Reihenfolge auflösen: Kommandozeilen-Flag, dann Konfigurationsdatei, dann eingebauter Standard.

#### Scenario: Flag und Datei widersprechen sich
- **WHEN** die Datei Konfidenz 0.5 nennt und `-c 0.6` übergeben wird
- **THEN** gilt 0.6

### Requirement: Prüfung beim Start
Das System SHALL die Konfiguration vor dem ersten Frame prüfen und bei einem Fehler mit klarer Meldung und Exit-Code ungleich 0 abbrechen. Fehler sind: unbekannter Schlüssel, falscher Typ, Ausschnitt außerhalb des Bildes, Haltezeit kleiner oder gleich 0, Wahrscheinlichkeit außerhalb 0 bis 1.

#### Scenario: Tippfehler im Schlüssel
- **WHEN** die Datei den unbekannten Schlüssel `hold_secs` enthält
- **THEN** bricht der Start ab
- **AND** die Meldung nennt den Schlüssel

#### Scenario: Ausschnitt ragt hinaus
- **WHEN** der Bildausschnitt über die Auflösung hinausreicht
- **THEN** bricht der Start ab

### Requirement: Warnung bei kurzer Haltezeit
Das System SHALL beim Start eine Warnung loggen, wenn die Haltezeit unter 3 Sekunden liegt. Es gibt keine Untergrenze, die den Start verhindert.

#### Scenario: Haltezeit 1 Sekunde
- **WHEN** die Konfiguration eine Haltezeit von 1 Sekunde enthält
- **THEN** startet das System
- **AND** loggt eine Warnung über die verkürzte Haltezeit

## MODIFIED Requirements

### Requirement: Kein dokumentierter Autostart
Das System SHALL im Repo keine Service-Definition und keinen Autostart mitbringen. Der Start des Hauptprogramms im Fahrzeug erfolgt manuell oder über einen nicht dokumentierten Mechanismus.

#### Scenario: Neustart des Rechners
- **WHEN** `hba1` neu startet
- **THEN** startet das Fernlicht-Programm nicht nachweislich von selbst

## REMOVED Requirements

### Requirement: Feste Werte im Code
**Reason**: Die Werte kommen künftig aus der Konfigurationsdatei und sind geprüft.
**Migration**: Ersetzt durch „Konfigurationsdatei", „Konfigurierbare Werte" und „Prüfung beim Start". Die eingebauten Standardwerte entsprechen den bisherigen festen Werten.
