## ADDED Requirements

### Requirement: Jedes Trainingsbild hat ein Label
Das System SHALL für jedes Bild im Trainingsset (`train`) eine Label-Datei verlangen. Eine leere Label-Datei ist nur für bewusste Negativbeispiele zulässig, erkennbar am Namenspräfix `OFF`. Ein Bild ohne Label-Datei gilt als Verstoß.

#### Scenario: Bild ohne Label
- **WHEN** ein Bild in `train/images/` keine zugehörige Label-Datei hat
- **THEN** meldet die Prüfroutine einen Verstoß

#### Scenario: Bewusstes Negativ
- **WHEN** ein Bild mit Präfix `OFF` eine leere Label-Datei hat
- **THEN** ist es kein Verstoß

#### Scenario: Leeres Label ohne Präfix
- **WHEN** eine leere Label-Datei zu einem Bild ohne Präfix `OFF` gehört
- **THEN** meldet die Prüfroutine einen Verstoß

### Requirement: Keine verwaisten Labels
Das System SHALL Label-Dateien ohne zugehöriges Bild als Verstoß melden.

#### Scenario: Label ohne Bild
- **WHEN** eine Label-Datei existiert, aber kein Bild mit gleichem Namen
- **THEN** meldet die Prüfroutine einen Verstoß

### Requirement: Einheitliche Klassen
Das System SHALL nur die Klassen `back` (Index 0) und `front` (Index 1) in kleingeschriebener Form zulassen. `data.yaml` und alle Label-Dateien SHALL zu dieser Reihenfolge passen.

#### Scenario: Unbekannter Klassenindex
- **WHEN** eine Label-Zeile den Klassenindex 2 enthält
- **THEN** meldet die Prüfroutine einen Verstoß

#### Scenario: Abweichende Schreibweise
- **WHEN** `data.yaml` die Klassennamen `Back` und `Front` enthält
- **THEN** meldet die Prüfroutine einen Verstoß

### Requirement: Gültige Label-Zeilen
Das System SHALL jede Label-Zeile als `<klasse> <x> <y> <b> <h>` mit vier Zahlen zwischen 0 und 1 prüfen und andere Zeilen als Verstoß melden.

#### Scenario: Wert außerhalb des Bereichs
- **WHEN** eine Label-Zeile die Breite 1,4 enthält
- **THEN** meldet die Prüfroutine einen Verstoß

### Requirement: Prüfung vor dem Training
Das System SHALL das Training verweigern, solange die Prüfroutine Verstöße meldet. Die Routine endet bei Verstößen mit Exit-Code ungleich 0 und listet jeden Verstoß mit Dateiname.

#### Scenario: Verstoß blockiert Training
- **WHEN** die Prüfroutine einen Verstoß findet
- **THEN** startet das Training nicht
- **AND** die Meldung nennt die betroffene Datei

### Requirement: Änderungsprotokoll
Das System SHALL jede Änderung am Trainingsset (neu gelabelt, korrigiert, entfernt) mit Dateiname, Grund und Datum in `DATASET_CHANGES.md` festhalten. Nach der Bereinigung SHALL für jedes der 456 ursprünglich unbeschrifteten Bilder die Entscheidung `geprüft` oder `verworfen` vermerkt sein.

#### Scenario: Bild entfernt
- **WHEN** ein unbeschriftetes Bild verworfen wird
- **THEN** steht es mit Grund im Protokoll
- **AND** es ist nicht mehr im Trainingsset

#### Scenario: Bild geprüft
- **WHEN** ein vorgelabeltes Bild von Jan geprüft wurde
- **THEN** steht es als `geprüft` im Protokoll
- **AND** sein Label liegt im Trainingsset

### Requirement: Vorlabels getrennt halten
Das System SHALL maschinell erzeugte Vorlabels in einem eigenen Ordner führen und erst nach der Prüfung durch einen Menschen ins Trainingsset übernehmen. Ungeprüfte Bilder SHALL nicht ins Trainingsset gelangen.

#### Scenario: Ungeprüftes Vorlabel
- **WHEN** ein Bild nur ein maschinelles Vorlabel hat
- **THEN** liegt es nicht in `train/`

### Requirement: Validierungs- und Testsatz bleiben unverändert
Das System SHALL `valid` und `test` bei der Bereinigung nicht verändern und neue Bilder ausschließlich nach `train` einordnen. Der Vergleich zwischen Modellen verwendet immer denselben `valid`- und `test`-Satz.

#### Scenario: Prüfsumme
- **WHEN** die Bereinigung abgeschlossen ist
- **THEN** stimmen die Prüfsummen von `valid` und `test` mit denen vor der Bereinigung überein

### Requirement: Abgesichertes Training
Das System SHALL ein Training nur auf `hba1` und erst nach bestandener GPU-Freigabe starten: 30 Minuten echte Inferenz mit `medium6` bei 65 W ohne Xid-Fehler und eine Probeepoche. Das Training SHALL in jeder Epoche einen Checkpoint schreiben und nach einem Abriss mit `resume` fortsetzbar sein.

#### Scenario: GPU-Freigabe nicht bestanden
- **WHEN** der Dauertest mit einem Xid-Fehler endet
- **THEN** startet kein Training

#### Scenario: Abriss während des Trainings
- **WHEN** die GPU nach Epoche 40 ausfällt
- **THEN** setzt `resume` das Training ab dem letzten Checkpoint fort

### Requirement: Abnahme eines neuen Modells
Das System SHALL ein neues Modell nur dann anstelle von `medium6` als Standard setzen, wenn auf demselben `valid`- und `test`-Satz alles gilt: Gesamt-Recall nicht schlechter, Recall der Klasse `front` nicht schlechter, mAP50 nicht schlechter, und die Frame-Zeit auf `hba1` im Median höchstens 0,15 s. `medium6` bleibt als Rückfall erhalten.

#### Scenario: Alle Kriterien erfüllt
- **WHEN** ein neues Modell bei Recall, Recall `front`, mAP50 und Frame-Zeit mindestens so gut ist wie `medium6`
- **THEN** darf es den Modellpfad der Konfiguration ersetzen

#### Scenario: Ein Kriterium verfehlt
- **WHEN** der Recall der Klasse `front` unter dem von `medium6` liegt
- **THEN** ersetzt das Modell `medium6` nicht
- **AND** der Befund wird dokumentiert
