# Tasks

## 1. Unit und Dokumentation im Repo

- [x] 1.1 `deploy/hba.service` nach Design schreiben und per `systemd-analyze verify` verifizieren, dass keine Fehler gemeldet werden (auf `hba1`, falls der Mac es nicht kann)
- [x] 1.2 Test schreiben, der in `deploy/hba.service` die Zeilen `Restart=on-failure`, `RestartSec=10`, `StartLimitIntervalSec=0`, `TimeoutStopSec=5`, `User=jkb` und das Fehlen einer `RequiresMountsFor`-Zeile prüft, und verifizieren, dass er besteht
- [x] 1.3 `deploy/README.md` mit Installation, Rückfall, Journal-Abfrage, Hinweis auf doppelten Start und der Beschreibung von `sensor.service` schreiben und verifizieren, dass die Befehle zum Ist-Zustand auf `hba1` passen
- [x] 1.4 Kopie der aktuellen Units von `hba1` als `deploy/hba.service.2024` und `deploy/sensor.service` ins Repo legen und verifizieren, dass sie dem Stand auf `hba1` entsprechen

## 2. Programm anschließen

- [x] 2.1 Logging zusätzlich auf stderr ausgeben (Journal) und verifizieren, dass ein Start ohne Ablagepfad die Meldungen auf stderr zeigt
- [x] 2.2 Fehlende oder ausgefallene Ablage (Datei-Log, Aufnahmen) auf WARNING und Abschalten statt Exception umstellen und verifizieren, dass „Stick fehlt beim Start", „Stick fällt im Betrieb aus" und „Ordner fehlen" als Tests bestehen, während Erkennung und Entscheidung weiterlaufen

## 3. Einrichtung auf `hba1` (nur nach Freigabe durch Jan)

- [x] 3.1 (Jan) Freigabe für die Systemänderung geben, danach alte Unit sichern, neue einspielen, `systemctl daemon-reload` und `restart`, und verifizieren, dass `systemctl status hba` und `journalctl -u hba` den Stand zeigen
- [x] 3.2 Ohne Stick und ohne Kamera starten und verifizieren, dass der Dienst kontrolliert scheitert, nach 10 s neu startet und nicht aufgibt
- [ ] 3.3 `kill -TERM` und `kill -KILL` auf den laufenden Prozess ausführen und verifizieren, dass TERM ohne Neustart endet und KILL nach 10 s einen Neustart auslöst
- [x] 3.4 Reboot-Test: `hba1` neu starten und verifizieren, dass der Dienst von selbst anläuft

## Workflow follow-up

- Reihenfolge beim Archivieren: `config-file` vor diesem Change (beide ändern „Kein dokumentierter Autostart", dieser entfernt sie).
- Danach `/opsx:archive`. Delta-Specs legen `service-supervision` neu an und ändern `runtime-configuration` und `data-collection`.
