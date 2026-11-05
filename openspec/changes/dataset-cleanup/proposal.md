# Proposal

## Why

Das Standardmodell `medium6` (YOLOv8-medium, Juni 2024) erreicht auf dem Validierungsset Precision 0,85, **Recall 0,87**, mAP50 0,88 und mAP50-95 0,45. Etwa jedes achte Fahrzeug wird dort nicht erkannt. Ein verpasstes Fahrzeug ist der gefährliche Fehlerfall. Im Fahrbetrieb fängt die 3-s-Haltezeit das meist ab, ein besserer Recall wäre trotzdem wertvoll.

Das Trainingsset `HBA4v2Dataset/train` hat dafür Mängel:
- 456 Roh-Captures (`<zeitstempel>.png`) ohne Label-Datei. YOLO wertet sie als Hintergrund, enthalten sie Fahrzeuge, wird dem Modell ein Fehler beigebracht.
- 4 verwaiste Label-Dateien ohne Bild.
- Uneinheitliche Klassenschreibweise (`Back/Front` und `back/front`) zwischen den Dataset-Versionen.
- 495 leere Labels (Präfix `OFF…`) sind gewollte Negativbeispiele und bleiben.

## What Changes

- Die 456 unannotierten Bilder werden von `medium6` **vorgelabelt**, von Jan in **Label Studio** (lokal) **geprüft** und je als `geprüft` oder `verworfen` entschieden. Keines bleibt als implizites Negativ im Set.
- Verwaiste Labels werden entfernt, Klassennamen vereinheitlicht und der Zustand des Datensatzes dokumentiert.
- Eine **Prüfroutine** stellt sicher, dass jedes Bild entweder ein Label hat oder bewusst ein leeres (Negativ).
- Danach wird ein neues Modell trainiert und gegen `medium6` verglichen, **Recall zuerst**. Ein neues Modell ersetzt `medium6` nur bei **strenger Abnahme**: Recall gesamt, Recall der Klasse `front`, mAP50 und Frame-Zeit je nicht schlechter, gemessen auf demselben `valid`- und `test`-Satz.
- Das Training läuft nur auf `hba1` und **erst, wenn die GPU einen Dauertest bestanden hat**. Es nutzt Checkpoints (`last.pt`, `resume`) und ein reduziertes Power-Limit, damit ein Abriss nicht den ganzen Lauf kostet.

## Capabilities

### New Capabilities
- `training-data`: Qualitätsregeln für den Trainingsdatensatz (jedes Bild hat ein Label oder ein bewusst leeres Label, einheitliche Klassen, keine Verwaisten) und Abnahmekriterien für ein neues Modell (Vergleich mit dem Standardmodell, Recall-Vorrang).

### Modified Capabilities
<!-- keine -->

## Impact

- **Daten:** `HBA4v2Dataset` auf dem Mac und auf `hba1` (Roboflow-Export `jkb-rzgt3/hba4`, Version 11); `valid` und `test` bleiben unverändert. Änderungen am Datensatz sind dokumentiert und rückverfolgbar.
- **Aufwand:** Das Prüfen der 456 Vorlabels ist Handarbeit (Label Studio).
- **Hardware:** Training nur auf `hba1`. Blockiert, bis die GPU unter Dauerlast stabil ist.
- **Voraussetzung:** keine Code-Abhängigkeit, kann parallel zu den anderen Changes laufen.
- **Nicht im Umfang:** Andere Modellarchitekturen, neue Klassen, zusätzliche Daten sammeln.
