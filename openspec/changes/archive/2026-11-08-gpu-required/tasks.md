# Tasks

## 1. Exit-Codes und Gerätewahl

- [x] 1.1 Exit-Code-Tabelle (0 bis 4) an einer Stelle definieren und verifizieren, dass ein Test jede Zuordnung gegen die Spec `runtime-configuration` prüft
- [x] 1.2 Standardgerät auf die erste GPU umstellen und `-d cpu` mit WARNING versehen und verifizieren, dass die Szenarien „Kein Flag" und „CPU ausdrücklich gewählt" als Tests bestehen

## 2. Start-Prüfung

- [x] 2.1 Start-Prüfung (CUDA verfügbar, Modell geladen, Warm-up mit 30 s Zeitlimit) im Detektor-Adapter umsetzen und per Fake verifizieren, dass „Keine GPU vorhanden", „Warm-up hängt" und „GPU in Ordnung" als Tests bestehen
- [x] 2.2 Bei Fehlschlag `0` senden, ERROR loggen und mit Exit-Code 3 enden und per Subprozess-Test mit Pseudo-Terminal verifizieren, dass `0\n` ankommt und der Exit-Code 3 ist

## 3. Betrieb

- [x] 3.1 CUDA-Fehler in der Inferenz auf den Pfad „`0` senden, Exit-Code 1" führen und per Fake-Detektor verifizieren
- [x] 3.2 Watchdog-Thread mit einspeisbarer Uhr und Abbruchfunktion umsetzen und verifizieren, dass „Hängende Inferenz" und „Normale Frame-Dauer" als Tests bestehen
- [x] 3.3 Subprozess-Test mit hängendem Fake-Detektor schreiben und verifizieren, dass der echte Prozess nach höchstens 6 s mit Exit-Code 4 endet und `0\n` zuletzt auf dem Pseudo-Terminal steht

## 4. Prüfung auf `hba1`

- [x] 4.1 Auf `hba1` die Warm-up-Dauer mit echter GPU messen und verifizieren, dass sie unter 30 s liegt (Wert in die Open Questions des Designs eintragen)
- [x] 4.2 Mit `CUDA_VISIBLE_DEVICES=` ohne GPU starten und verifizieren, dass das Programm mit Exit-Code 3 endet und `0` sendet
- [x] 4.3 Auf `hba1` mit Test-Schalter eine hängende Inferenz erzeugen (kein `SIGSTOP`, das würde auch den Watchdog-Thread anhalten) und verifizieren, dass der Prozess nach höchstens 6 s mit Exit-Code 4 endet und `0` auf dem Pseudo-Terminal steht

## Workflow follow-up

- Nach dem Review archivieren (`/opsx:archive`). Delta-Specs aktualisieren `object-detection` und `runtime-configuration`.
- Neustart bei Exit-Code ungleich 0 setzt `systemd-service` voraus.
