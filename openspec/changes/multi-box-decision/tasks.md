# Tasks

## 1. Testdaten

- [ ] 1.1 `tools/extract_replay.py` schreiben, das aus den Roh-Logs die Frame-Auszüge als `jsonl.gz` erzeugt, und auf `hba1` verifizieren, dass Frame-Anzahl (22.900 und 21.936) und Statuswechsel (178 und 108) mit den Roh-Logs übereinstimmen
- [ ] 1.2 Auszüge nach `tests/data/` übernehmen und verifizieren, dass sie zusammen unter 1 MB liegen und der Mac sie vollständig einlesen kann

## 2. Tests (zuerst, rot)

- [ ] 2.1 Test „Nachbau alt gleich geloggt" auf beiden Auszügen schreiben (Referenzimplementierung der alten Logik im Testcode) und verifizieren, dass er 0 Abweichungen meldet
- [ ] 2.2 Szenarien-Tests aus der Delta-Spec („Zweites Fahrzeug relevant, erstes nicht", „Erstes relevant, zweites nicht", „Keine Box relevant") schreiben und verifizieren, dass sie gegen die alte Logik fehlschlagen (erstes Szenario)
- [ ] 2.3 Replay-Test „neu <= alt" auf beiden Auszügen schreiben
- [ ] 2.4 Property-Test mit Zufallsfolgen (feste Seeds, Boxen mit Konfidenzen oberhalb des Schwellwerts, Zeitpunkte mit Sprüngen) für „neu <= alt" schreiben

## 3. Umsetzung

- [ ] 3.1 Entscheidungsmodul auf „irgendeine Box relevant" umstellen, Legacy-Kommentar entfernen, und verifizieren, dass alle Tests aus Gruppe 2 bestehen
- [ ] 3.2 Tests auf `hba1` unter Python 3.10 ausführen und verifizieren, dass alle bestehen

## Workflow follow-up

- Nach dem Review archivieren (`/opsx:archive`). Dabei ersetzt die Delta-Spec die Legacy-Requirement in `openspec/specs/high-beam-decision/`.
