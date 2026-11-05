## MODIFIED Requirements

### Requirement: Vorbereiteter Speicherort
Das System SHALL voraussetzen, dass die Ordner `log/`, `labels/detections/`, `images/crop/`, `images/random/` und `images/detections/` unter dem Pfad (Standard `/mnt/hba-stick/HBA/`) bereits existieren. Es legt sie nicht an. Fehlt die Ablage, SHALL das System die betroffenen Aufnahmen abschalten und weiterlaufen (siehe Spec `runtime-configuration`).

#### Scenario: Ordner fehlen
- **WHEN** ein benötigter Ordner nicht existiert
- **THEN** loggt das System einen WARNING
- **AND** die betroffene Aufnahme entfällt
- **AND** die Erkennung läuft weiter
