# Design

## Context

Ausgangslage auf `hba1` (gelesen am 2026-11-06):

```
hba.service     enabled seit Juli 2024, Status "failed"
                ExecStart=/usr/bin/python3 /home/jkb/yolov8.py -d 0   User=jkb
                kein Restart=, keine Mount-Abhaengigkeit
                Absturz beim Boot: FileNotFoundError /mnt/hba-stick/HBA/log/...
sensor.service  enabled, aktiv, ExecStart=/usr/bin/python3 /home/jkb/nvidia1.py
```

Der Autostart existiert also, hält aber nach dem ersten Fehler nicht an. Der Benutzer `jkb` ist in `dialout` (Serial). Zum Zeitpunkt der Messung waren Kamera und Mikrocontroller nicht angeschlossen. Dieser Change repariert die Unit und legt ihren Inhalt ins Repo. Er braucht `fail-safe-shutdown` (Exit-Codes, SIGTERM) und `gpu-required` (Exit-Codes 3 und 4).

## Goals / Non-Goals

**Goals:**
- Der Assistent läuft nach jedem Boot und nach jedem Fehler wieder an, ohne Eingriff.
- Der Dienst hängt von nichts ab, was fehlen kann (Stick, Netzwerk).
- Die Unit ist versioniert und prüfbar.

**Non-Goals:**
- Kein GPU-Rescan beim Boot, keine Änderung an `sensor.service` oder der Telemetrie, keine externe Überwachung.

## Decisions

### 1. Vorhandene Unit reparieren, nicht neu erfinden

Name, Benutzer und Pfad des Programms bleiben. Neu sind die Neustart-Regel und der kontrollierte Stopp. Die Unit lautet im Kern:

```
[Unit]
Description=HBA High Beam Assist
StartLimitIntervalSec=0

[Service]
User=jkb
ExecStart=<venv>/bin/python -m hba -d 0 --config /home/jkb/hba.yaml
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=10
TimeoutStopSec=5
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
```

Der genaue `ExecStart` hängt vom Paket aus `modular-pipeline` ab (Pfad der virtuellen Umgebung) und wird bei der Einrichtung eingesetzt.

### 2. Endloser Neustart mit 10 s Wartezeit

Entscheidung von Jan. `StartLimitIntervalSec=0` hebt die systemd-Sperre auf (sonst gibt systemd nach 5 Fehlstarts in 10 s auf). Bei Dauerfehler entsteht nur Log-Rauschen alle 10 s. Das Licht bleibt dabei abgeblendet. Die 10 s verhindern eine enge Schleife und geben der GPU Zeit zu erscheinen.

*Verworfen:* begrenzte Versuche. Eine GPU, die erst später erkannt wird, wäre dann für den Rest der Fahrt verloren.

### 3. Keine Abhängigkeit vom Stick

Entscheidung von Jan: Der Dienst startet auch ohne `/mnt/hba-stick`. Das Programm schaltet dann Datei-Log und Aufnahmen ab (Delta in `runtime-configuration` und `data-collection`) und loggt ins Journal. Das legacy-Verhalten (Exception und Ende) war die Ursache des heutigen Ausfalls.

### 4. Journal als Standard-Log

systemd leitet stdout und stderr ins Journal. Das Programm muss dafür zusätzlich auf stderr loggen, zum Beispiel über einen `StreamHandler`. Das geschieht in der Pipeline, nicht in der Unit.

### 5. Kein WatchdogSec

Den Watchdog übernimmt das Programm selbst (`gpu-required`). `WatchdogSec` von systemd kann später ergänzend kommen.

### 6. Prüfung der Unit ohne Installation

`systemd-analyze verify deploy/hba.service` und ein Test, der die Schlüsselzeilen prüft, laufen ohne sudo. Der echte Neustart-Test läuft auf `hba1` erst nach ausdrücklicher Freigabe.

### 7. Installation ist eine bestätigte Systemänderung

Die Einrichtung ersetzt `/etc/systemd/system/hba.service` und braucht sudo. Vorher sichert sie die alte Unit als `hba.service.bak-<datum>`. Rückfall ist `cp` zurück und `systemctl daemon-reload`.

## Risks / Trade-offs

- **Dauerschleife bei dauerhaftem Fehler** → Bewusst akzeptiert. Journal-Rauschen ist harmlos. Das Fernlicht bleibt aus.
- **Neustart überfährt eine laufende Fahrt** → Ein Neustart bedeutet einige Sekunden Abblendlicht (Warm-up plus Firmware-Timeout), das ist die sichere Richtung.
- **Aufnahmen gehen unbemerkt verloren, wenn der Stick fehlt** → WARNING im Journal. Wer Daten sammeln will, prüft das Journal. Eine automatische Meldung ist nicht im Umfang.
- **Doppelter Start (Dienst und manueller Lauf)** → Zwei Prozesse auf demselben Serial-Port. Die README weist darauf hin, den Dienst vor manuellen Tests zu stoppen.
- **Die alte Unit zeigt auf `/home/jkb/yolov8.py`** → Die neue Unit startet das Paket. Bis dahin bleibt die alte Unit wirksam. Umstellung erst, wenn der Vergleichslauf aus `modular-pipeline` bestanden ist.

## Migration Plan

1. Unit und README im Repo schreiben und ohne sudo prüfen.
2. Auf `hba1` mit Freigabe: alte Unit sichern, neue einspielen, `daemon-reload`, `systemctl restart hba`.
3. Prüfen: Dienst aktiv, `journalctl -u hba` zeigt Meldungen. Ohne Stick, Kamera und Mikrocontroller scheitert der Start kontrolliert und der Dienst versucht es weiter.
4. Neustart-Test: `kill -TERM` prüfen (Exit 0, kein Neustart), danach Prozess mit `kill -KILL` abschießen (Neustart nach 10 s).

Rollback: gesicherte Unit zurückkopieren.

## Open Questions

- Pfad der virtuellen Umgebung auf `hba1` (ergibt sich aus `modular-pipeline`).
- Soll `sensor.service` ebenfalls `Restart=on-failure` bekommen? Nicht im Umfang, aber billig nachzuziehen.
