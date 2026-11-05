# Tasks

## 1. Repository und Gerüst

- [x] 1.1 `git init`, `.gitignore` (Modelle `*.pt`, Datensätze, Logs, virtuelle Umgebungen, `__pycache__`) und ersten Commit anlegen und verifizieren, dass `git status` sauber ist und keine Modell- oder Datensatzdatei erfasst wird
- [x] 1.2 `pyproject.toml` (Python ab 3.10, Extras `dev` und `gpu`), `src/hba/__init__.py` und `tests/` anlegen und verifizieren, dass `pip install -e ".[dev]"` und `pytest` ohne Fehler durchlaufen
- [x] 1.3 `README.md` mit Einrichtung, Testlauf und Deploy auf `hba1` schreiben und verifizieren, dass die dokumentierten Befehle auf dem Mac wie beschrieben laufen
- [x] 1.4 (Jan) Privates GitHub-Repo anlegen, `origin` setzen, Deploy-Key auf `hba1` einrichten und verifizieren, dass `git pull` auf `hba1` funktioniert

## 2. Ports und Fakes

- [x] 2.1 Schnittstellen `Camera`, `Detector`, `Actuator`, `Clock` und den Datentyp `Box` in `src/hba/ports.py` definieren und verifizieren, dass das Modul ohne OpenCV, Torch und Serial importierbar ist
- [x] 2.2 `tests/fakes.py` mit Fake-Kamera (Bildfolge), Fake-Detektor (programmierte Boxen), Fake-Aktor (zeichnet Status auf) und Fake-Uhr schreiben und verifizieren, dass ein Test eine programmierte Sequenz unverändert abspielt

## 3. Reine Logik

- [x] 3.1 Bildaufbereitung (Drehen um 180°, Zuschnitt `[0:850]` und `[212:638, 400:1360]`, Resize 640×640 mit INTER_AREA) in `capture.py` umsetzen und per Golden-Test verifizieren, dass das Ergebnis Pixel für Pixel dem Legacy-Slicing auf einem Testbild entspricht
- [x] 3.2 Relevanzfilter (Breite < 500, obere Kante > 160) in `relevance.py` umsetzen und verifizieren, dass die Szenarien aus der Spec `relevance-filter` als Tabellentest bestehen
- [x] 3.3 Entscheidungsfunktion in `decision.py` mit allen Legacy-Eigenheiten (Start abgeblendet für 3 s, Drosselung auf eine Aktualisierung pro Sekunde, erste Box, sofortiges Abblenden, Aufblenden nach 3 s) umsetzen und verifizieren, dass die Szenarien aus der Spec `high-beam-decision` einschließlich „Zweites Fahrzeug relevant, erstes nicht" als Tests bestehen

## 4. Datensammlung und Monitoring

- [x] 4.1 Recorder in `recorder.py` umsetzen (Zeitstempel-Namen, Ausschnitte mit `-s`, 1 % Stichproben, 9 % Detektionsbeispiele, Limit 1000, YOLO-Label der ersten Box) und mit festem Zufalls-Seed in einem temporären Ordner verifizieren, dass Dateinamen, Limit und Label-Zeile der Spec `data-collection` entsprechen
- [x] 4.2 Monitoring in `monitor.py` umsetzen (Logdatei im Legacy-Format, Boxfarben gelb/rot/weiß mit 13 Pixel Abstand, Stream-Dateien in `/tmp`) und verifizieren, dass Logzeilen und Boxfarben (Pixelprobe) der Spec `monitoring` entsprechen

## 5. Adapter

- [ ] 5.1 Kamera-Adapter in `capture.py` umsetzen (OpenCV, MJPG, 1920×1080, `v4l2-ctl`-Einstellungen wie im Original) und auf `hba1` verifizieren, dass `initialize_camera: OK` geloggt wird und ein 1920×1080-Frame ankommt
- [x] 5.2 Detektor-Adapter in `detect.py` mit verzögertem Import umsetzen und verifizieren, dass ein Test auf dem Mac nachweist, dass der Import des Moduls weder `torch` noch `ultralytics` lädt, und dass `hba1` mit `medium6` für ein Testbild Boxen liefert
- [x] 5.3 Einfachen Serial-Aktor wie im Original (je Frame `1\n` oder `0\n`, Port und Baudrate wie in der Spec) in `actuator.py` umsetzen und per Pseudo-Terminal-Test verifizieren, dass die richtigen Bytes ankommen

## 6. Hauptschleife und Aufruf

- [x] 6.1 Hauptschleife in `app.py` aus den Ports zusammensetzen und per Ende-zu-Ende-Test mit Fake-Kamera, Fake-Detektor und Pseudo-Terminal verifizieren, dass eine programmierte Frame-Folge die erwartete Statusfolge liefert
- [x] 6.2 Alle Flags mit den Standardwerten der Baseline in `cli.py` und den Einstieg `python -m hba` umsetzen und verifizieren, dass `python -m hba --help` alle zehn Flags zeigt und ein Test die Standardwerte prüft
- [x] 6.3 Minimalen Lebenszyklus wie im Original (SIGINT, `---END---`, Exit-Code 0 bei unbehandelten Fehlern, Taste `c`) in `lifecycle.py` umsetzen und per Subprozess-Test verifizieren, dass Signal und Exception das Programm wie in der Spec `runtime-configuration` beschrieben beenden

## 7. Prüfung auf `hba1`

- [x] 7.1 Auf `hba1` klonen, Umgebung mit `--system-site-packages` einrichten und verifizieren, dass `pytest` unter Python 3.10 vollständig besteht
- [x] 7.2 Fünf Minuten mit Bildordner statt Kamera (`hba.replay.FolderCamera`, `tools/replay_run.py`), GPU (`-d 0`) und Pseudo-Terminal laufen lassen und verifizieren, dass das Log dieselben Meldungstypen wie die Legacy-Logs enthält und die Frame-Dauer im Median bei höchstens 0,15 s liegt (gemessen 2026-11-06: 3.853 Frames, Median 0,075 s, Maximum 0,118 s, kein Xid)
- [ ] 7.3 Fünf Minuten mit echter Kamera, GPU und Pseudo-Terminal (oder Mikrocontroller) laufen lassen und verifizieren, dass `initialize_camera: OK` im Log steht und die Frame-Dauer im Median bei höchstens 0,15 s liegt

## Workflow follow-up

- Change nach dem Review archivieren (`/opsx:archive`). Da keine Delta-Specs existieren, ändern sich die Specs in `openspec/specs/` nicht.
- Danach `fail-safe-shutdown` Gruppe 4 und die weiteren Changes auf dem neuen Gerüst fortsetzen.
