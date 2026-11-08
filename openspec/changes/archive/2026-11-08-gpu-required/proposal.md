# Proposal

## Why

Der Standard für das Rechengerät ist `cpu` (`-d cpu`). Alle echten Fahrt-Läufe in den Logs nutzten ausdrücklich die GPU (`-d 0`). Auf dem i3-5010U dauert ein Frame mit YOLOv8-medium Sekunden. Das ist im Betrieb unbrauchbar, und die Staleness-Regel aus `fail-safe-shutdown` würde dort fast immer `0` erzwingen.

Hinzu kommt die Hardware-Realität auf `hba1`: Die GPU wird beim Boot nicht immer erkannt, und unter Last kann sie vom PCIe-Bus fallen (Xid 79). Nach einem GPU-Fehler lässt sich CUDA im selben Prozess in der Regel nicht neu initialisieren.

Weil das Relais nur freigibt (Freigabe in Reihe mit dem Lichthebel), ist ein Ausfall ungefährlich: Der Fahrer fährt dann mit Abblendlicht.

## What Changes

- Das Standardgerät ist die GPU. Die CPU gibt es nur auf ausdrückliche Anforderung, etwa für Entwicklung und Tests auf dem Mac, mit deutlicher Warnung.
- Beim Start prüft das System, ob eine nutzbare GPU vorhanden ist. Fehlt sie, loggt es einen ERROR, sendet `0` und **beendet sich mit einem eigenen Exit-Code**.
- Ein Dienst-Manager startet das Programm mit Wartezeit neu und prüft die GPU bei jedem Versuch (siehe `systemd-service`).
- Fällt die GPU im Betrieb aus (CUDA-Fehler), gilt der Pfad aus `fail-safe-shutdown`: `0` senden, mit Fehlercode beenden, Neustart durch den Dienst.
- Ein **Watchdog-Thread** erkennt eine hängende Inferenz (Xid 79 kann CUDA-Aufrufe blockieren statt Fehler zu melden): Länger als 5 s ohne fertigen Frame, dann `0` senden und hart beenden (Exit-Code 4).
- Feste **Exit-Codes**: 0 Stopp, 1 Fehler, 2 Konfiguration, 3 keine GPU, 4 Watchdog.
- Die Start-Prüfung umfasst CUDA, Modell auf der GPU und einen Warm-up-Frame (30 s Zeitlimit).
- **BREAKING:** Der Standardwert von `-d` ändert sich von `cpu` auf die GPU.

## Capabilities

### New Capabilities
<!-- keine -->

### Modified Capabilities
- `object-detection`: Standardgerät GPU, Start-Prüfung, Verhalten ohne nutzbare GPU, Watchdog.
- `runtime-configuration`: Exit-Code-Tabelle, Standardwert von `-d`.

## Impact

- **Code:** Gerätewahl und Start-Prüfung im Erkennungsmodul.
- **Betrieb:** Setzt den Dienst aus `systemd-service` voraus, damit ein Neustart nach dem Beenden automatisch erfolgt.
- **Voraussetzungen:** `fail-safe-shutdown` (Exit-Codes, Abblenden beim Beenden), `modular-pipeline`.
- **Nicht im Umfang:** CPU-Fallback, Neuinitialisierung von CUDA im selben Prozess, Behebung der GPU-Hardwareprobleme (Stromversorgung, Riser), Boot-Rescan der GPU.
