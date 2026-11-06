# Tasks

## 1. Konfiguration

- [x] 1.1 Konfigurationsmodell mit allen Standardwerten der Baseline in `config.py` schreiben und per Test verifizieren, dass ein Start ohne Datei exakt die Legacy-Werte ergibt
- [x] 1.2 Laden aus YAML mit `ruamel.yaml`, Vorrang Flag vor Datei vor Standard und Pfadauflösung (`--config`, `./hba.yaml`) umsetzen und verifizieren, dass die Szenarien „Start ohne Datei", „Angegebene Datei fehlt" und „Flag und Datei widersprechen sich" als Tests bestehen
- [x] 1.3 Prüfung beim Start umsetzen (unbekannte Schlüssel, Typen, Bereiche, Ausschnitt innerhalb des Bildes, Sammelmeldung, Exit-Code 2) und verifizieren, dass „Tippfehler im Schlüssel" und „Ausschnitt ragt hinaus" als Tests bestehen
- [x] 1.4 Warnung bei Haltezeit unter 3 s umsetzen und verifizieren, dass der Start mit 1 s gelingt und die Warnung im Log steht, während 0 s und −1 s abbrechen
- [x] 1.5 Beim Start die effektiven Werte mit Quelle (Flag, Datei, Standard) loggen und verifizieren, dass jede Quelle in einem Test erscheint
- [x] 1.6 `config/hba.example.yaml` schreiben und per Test verifizieren, dass sie geladen die eingebauten Standardwerte ergibt

## 2. Pipeline anschließen

- [x] 2.1 Bildaufbereitung (Drehung, `hood_rows`, Ausschnitt, Auflösung) auf die Konfiguration umstellen und per Golden-Test verifizieren, dass die Standardwerte Pixel für Pixel das bisherige Ergebnis liefern und ein geänderter Ausschnitt die erwartete Größe hat
- [x] 2.2 Relevanzfilter und Haltezeit (einschließlich Start) auf die Konfiguration umstellen und verifizieren, dass die geänderten Szenarien aus den Delta-Specs und der Replay-Test aus `multi-box-decision` mit Standardwerten unverändert bestehen
- [x] 2.3 Serial-Port, Baudrate, Stichproben-Wahrscheinlichkeiten und Dateilimit umstellen und verifizieren, dass ein Pseudo-Terminal-Test den konfigurierten Port nutzt

## 3. Kalibrier-Werkzeug

- [ ] 3.1 Rechteck-Geometrie, Koordinatenumrechnung (Anzeige zu Bild und zurück) und Prüfung in `calibration.py` schreiben und per Tabellentest verifizieren
- [ ] 3.2 Schreiben in die YAML-Datei (atomar, nur geänderte Schlüssel, Kommentare bleiben) umsetzen und per Test verifizieren, dass ein Round-Trip eine Datei mit Kommentaren bis auf die geänderten Werte byte-identisch lässt
- [ ] 3.3 OpenCV-Fenster in `calibrate.py` mit Maus, Tasten `s` und `q` und Einstiegspunkt `python -m hba.calibrate` (`--image`, `--camera`, `--config`) umsetzen und verifizieren, dass der Smoke-Test ohne Display die Argumente und die Fehlermeldung bei fehlendem Bild prüft
- [ ] 3.4 (Jan) Handtest auf dem Mac mit einem Testbild: Ausschnitt verschieben, speichern, Datei prüfen, und verifizieren, dass die Anzeige der Standardwerte den 960×426-Ausschnitt zeigt

## 4. Dokumentation und Prüfung

- [ ] 4.1 README um Konfiguration, Prüfmeldungen und Kalibrierung ergänzen und verifizieren, dass die Befehle wie beschrieben laufen
- [ ] 4.2 Auf `hba1` unter Python 3.10 klonen, `pytest` ausführen und einen Kurzlauf mit Beispiel-Konfiguration fahren, und verifizieren, dass der Status gleich der Legacy-Folge für denselben Testlauf ist

## Workflow follow-up

- Nach dem Review archivieren (`/opsx:archive`). Delta-Specs aktualisieren `camera-calibration` (neu), `runtime-configuration`, `image-capture`, `relevance-filter` und `high-beam-decision`.
