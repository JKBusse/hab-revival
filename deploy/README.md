# Dienst-Einrichtung auf hba1

Dateien in diesem Ordner:

| Datei | Zweck |
|---|---|
| `hba.service` | Neue Unit für den Fernlicht-Assistenten (Neustart bei Fehlern, kontrollierter Stopp) |
| `hba.service.2024` | Die bisherige Unit, **nur zur Dokumentation** (Stand gelesen am 2026-11-06) |
| `sensor.service` | Die Telemetrie-Unit (`nvidia1.py`), **unverändert**, nur dokumentiert |

## Ausgangslage (2026-11-06)

`hba.service` ist seit Juli 2024 aktiviert, hat aber **keine Neustart-Regel**. Sie stand auf „failed",
weil `/mnt/hba-stick` beim Boot nicht eingehängt war und das Programm beim Anlegen der Logdatei
abstürzte. `sensor.service` (MQTT-Telemetrie) läuft zuverlässig.

## Was die neue Unit anders macht

- `Restart=on-failure`, `RestartSec=10`, `StartLimitIntervalSec=0`: Bei jedem Exit-Code ungleich 0
  (zum Beispiel 3 = keine GPU, 4 = Watchdog) startet der Dienst nach 10 s neu, **endlos**.
- `KillSignal=SIGTERM`, `TimeoutStopSec=5`: Ein gewollter Stopp sendet SIGTERM. Das Programm sendet
  `0` ans Relais und beendet mit Exit-Code 0, dann gibt es keinen Neustart. Nach 5 s folgt SIGKILL.
- **Keine Abhängigkeit vom USB-Stick** und vom Netzwerk. Fehlt der Stick, läuft die Erkennung weiter,
  das Programm warnt, und Datei-Log und Aufnahmen entfallen.
- Das Programm läuft aus dem Paket (`python -m hba`) mit dem Arbeitsverzeichnis `~/hba-revival`.
  Dort wird `./hba.yaml` gelesen, falls vorhanden.

## Installation (ändert das System, braucht sudo)

> Diese Schritte ersetzen eine Systemdatei. Sie laufen erst nach ausdrücklicher Freigabe durch Jan.
> Vorher prüfen: `systemd-analyze verify deploy/hba.service`.

```bash
# 1. alte Unit sichern
sudo cp /etc/systemd/system/hba.service /etc/systemd/system/hba.service.bak-$(date +%F)

# 2. neue Unit einspielen und laden
sudo cp ~/hba-revival/deploy/hba.service /etc/systemd/system/hba.service
sudo systemctl daemon-reload

# 3. starten und prüfen
sudo systemctl restart hba
systemctl status hba --no-pager
journalctl -u hba -n 50 --no-pager
```

**Rückfall:**

```bash
sudo cp /etc/systemd/system/hba.service.bak-<datum> /etc/systemd/system/hba.service
sudo systemctl daemon-reload && sudo systemctl restart hba
```

## Betrieb

```bash
systemctl status hba            # Zustand
journalctl -u hba -f            # Meldungen live
sudo systemctl stop hba         # gewollter Stopp: sendet 0, kein Neustart
sudo systemctl restart hba
```

- **Journal:** Es enthält Start-Meldungen, Konfiguration, Warnungen und Fehler, aber **nicht** den
  Takt jedes Frames (sonst Flut). Die vollständige Datei steht unter `<Ablage>/log/`, solange der
  Stick eingehängt ist.
- **Doppelter Start:** Vor manuellen Tests mit dem Serial-Port den Dienst anhalten
  (`sudo systemctl stop hba`). Zwei Prozesse auf `/dev/ttyUSB0` stören sich.
- **Dauerfehler:** Ist die GPU dauerhaft weg, startet der Dienst alle 10 s neu und loggt jedes Mal
  den Grund. Das Licht bleibt dabei abgeblendet. Das ist gewollt.

## Telemetrie (`sensor.service`)

Sendet jede Sekunde CPU- und GPU-Messwerte per MQTT. Diese Unit hat ebenfalls kein `Restart=`.
Eine Änderung ist nicht Teil dieses Changes (bei Bedarf `Restart=on-failure` ergänzen).
