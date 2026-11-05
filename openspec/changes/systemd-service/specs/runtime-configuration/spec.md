## ADDED Requirements

### Requirement: Ablage nicht verfügbar
Das System SHALL bei fehlendem oder nicht beschreibbarem Ablagepfad (Logs, Bilder, Labels) einen WARNING loggen, Datei-Log und Aufnahmen abschalten und die Erkennung samt Entscheidung unverändert weiterlaufen lassen. Ein Schreibfehler im Betrieb schaltet nur die betroffene Ablage ab, mit einem WARNING und ohne das Programm zu beenden.

#### Scenario: Stick fehlt beim Start
- **WHEN** `/mnt/hba-stick/HBA/` nicht existiert
- **THEN** startet das Programm trotzdem
- **AND** ein WARNING nennt den fehlenden Pfad
- **AND** die Meldungen stehen im Journal statt in einer Datei

#### Scenario: Stick fällt im Betrieb aus
- **WHEN** ein Schreibvorgang für ein Bild fehlschlägt
- **THEN** werden die Aufnahmen abgeschaltet
- **AND** die Erkennung läuft weiter

## REMOVED Requirements

### Requirement: Kein dokumentierter Autostart
**Reason**: Die Annahme war falsch. Auf `hba1` existiert seit Juli 2024 eine `hba.service`, die beim Boot startet, aber ohne Neustart-Regel nach dem ersten Fehler stehen bleibt.
**Migration**: Ersetzt durch die Spec `service-supervision`.
