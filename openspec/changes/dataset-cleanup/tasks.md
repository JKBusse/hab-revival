# Tasks

## 1. Prüfroutine und Ist-Zustand

- [x] 1.1 Unveränderte Sicherungskopie von `HBA4v2Dataset` anlegen und verifizieren, dass Dateianzahl und Prüfsummen mit dem Original übereinstimmen
- [x] 1.2 `tools/check_dataset.py` mit allen Regeln aus der Spec `training-data` (Label für jedes Bild, leer nur bei `OFF`, Verwaiste, Klassen, Wertebereiche) schreiben und per Tabellentest mit kleinen Beispiel-Datensätzen verifizieren, dass jedes Szenario erkannt wird
- [x] 1.3 Routine auf dem echten Datensatz laufen lassen und verifizieren, dass sie die bekannten Mängel meldet (456 Bilder ohne Label, 4 verwaiste Labels). Befund 2026-11-06: Die Klassenschreibweise in `HBA4v2Dataset` war bereits richtig, dazu kamen 8 leere Labels ohne Präfix `OFF` (siehe 2.1)
- [x] 1.4 Prüfsummen von `valid` und `test` festhalten (`--checksums`) und verifizieren, dass ein erneuter Lauf dieselben Werte liefert

## 2. Einfache Bereinigung

- [x] 2.1 Die 4 verwaisten Labels entfernen und Klassenschreibweise vereinheitlichen, jede Änderung in `DATASET_CHANGES.md` festhalten, und verifizieren, dass die Prüfroutine nur noch die 456 Bilder meldet

## 3. Vorlabeln und Prüfen

- [x] 3.1 Skript für Vorlabels (`medium6`, Schwelle 0,25, Ausgabe nach `prelabel/`) schreiben und auf `hba1` verifizieren, dass für alle 456 Bilder je eine Label-Datei (ggf. leer) entsteht
- [x] 3.2 `yolo_to_ls.py` und `ls_to_yolo.py` schreiben und per Rundreise-Test verifizieren, dass YOLO → Label Studio → YOLO dieselben Zeilen bis auf Rundung ergibt
- [x] 3.3 (Jan) Label Studio in eigener venv (Python 3.11 oder 3.12) einrichten, Bilder und Vorlabels importieren und verifizieren, dass ein Bild mit Rahmen angezeigt wird
- [x] 3.4 (Jan) Alle 456 Bilder prüfen und je als `geprüft` oder `verworfen` entscheiden und verifizieren, dass kein Bild ohne Entscheidung bleibt
- [x] 3.5 Ergebnis exportieren, geprüfte Bilder nach `train/` übernehmen, verworfene entfernen, Protokoll ergänzen, und verifizieren, dass die Prüfroutine fehlerfrei durchläuft und `valid`/`test` dieselben Prüfsummen haben
- [ ] 3.6 Stichprobe von 20 geprüften Bildern zufällig ziehen und Jan zur Gegenprüfung zeigen, und verifizieren, dass die Fehlerquote im Protokoll steht

## 4. GPU-Freigabe

- [x] 4.1 (Jan) Zustimmung für `nvidia-smi -pl 65` (sudo) auf `hba1` geben
- [x] 4.2 30 Minuten echte Inferenz mit `medium6` bei 65 W laufen lassen und verifizieren, dass im Kernel-Log kein Xid-Fehler steht und Leistung, Temperatur und Takt aufgezeichnet sind
- [x] 4.3 Eine Probeepoche trainieren und verifizieren, dass der Lauf ohne GPU-Abriss endet und die Dauer pro Epoche notiert ist

## 5. Training und Abnahme

- [ ] 5.1 Einstellungen aus `medium6/args.yaml` lesen, Abweichungen begründen und verifizieren, dass das Protokoll sie nennt
- [ ] 5.2 Training detached mit `save_period=1` starten und verifizieren, dass nach der ersten Epoche ein Checkpoint existiert und `resume` im Probelauf funktioniert
- [ ] 5.3 Neues Modell und `medium6` auf demselben `valid`- und `test`-Satz auswerten und verifizieren, dass Recall gesamt, Recall `front`, mAP50 und Frame-Zeit (Median, `hba1`) in einer Tabelle stehen
- [ ] 5.4 Abnahme nach der Spec entscheiden, Befund dokumentieren und bei Erfolg den Modellpfad in der Konfiguration umstellen, andernfalls `medium6` belassen

## Workflow follow-up

- Nach dem Review archivieren (`/opsx:archive`). Die Delta-Spec legt `training-data` neu an.
- Die Umstellung des Modellpfads setzt `config-file` voraus.
