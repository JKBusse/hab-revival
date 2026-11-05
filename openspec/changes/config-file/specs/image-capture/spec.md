## MODIFIED Requirements

### Requirement: Bildausrichtung
Das System SHALL jedes Bild um 180° drehen, wenn die Konfiguration `rotate_180` auf wahr steht (Standard wahr, weil die Kamera kopfüber montiert ist).

#### Scenario: Frame erfasst
- **WHEN** ein Frame gelesen wurde und `rotate_180` wahr ist
- **THEN** wird er um 180° gedreht, bevor er weiterverarbeitet wird

#### Scenario: Kamera aufrecht montiert
- **WHEN** `rotate_180` auf falsch steht
- **THEN** wird das Bild nicht gedreht

### Requirement: Bildausschnitt für die Erkennung
Das System SHALL aus dem gedrehten Bild die Zeilen bis `hood_rows` (Standard 850) behalten und daraus den konfigurierten Erkennungsausschnitt wählen (Standard Zeilen 212–638, Spalten 400–1360). Der Ausschnitt SHALL mit INTER_AREA auf 640×640 skaliert werden. Die Seitenverhältnisse werden nicht erhalten.

#### Scenario: Ausschnitt und Skalierung
- **WHEN** ein gedrehter 1920×1080-Frame vorliegt und die Standardwerte gelten
- **THEN** entsteht ein 960×426-Ausschnitt
- **AND** daraus ein 640×640-Eingabebild

#### Scenario: Geänderter Ausschnitt
- **WHEN** die Konfiguration Spalten 300–1300 nennt
- **THEN** ist der Ausschnitt 1000 Pixel breit
