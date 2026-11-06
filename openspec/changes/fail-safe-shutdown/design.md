# Design

## Context

Motivation und Umfang stehen in `proposal.md`. Die Anforderungen stehen in den Delta-Specs zu `actuator-control` und `runtime-configuration`.

Ausgangslage im Legacy-Code (`legacy/yolov8.py`): Der Status wird in der Hauptschleife berechnet und dort direkt auf die serielle Schnittstelle geschrieben. Es gibt keinen zweiten Ausführungsstrang. Hängt die Hauptschleife (zum Beispiel in CUDA oder `camera.read()`), sendet niemand mehr etwas. Die Firmware blendet dann nach 1 bis 3 Sekunden ab. Gemessene Frame-Dauer auf der GPU: Median 0,08 bis 0,12 s, Maximum 0,16 s, bei etwa 130.000 Frames kein Frame über 1 s.

Randbedingungen: Firmware-Timeout 1 bis 3 s (nicht änderbar), Protokoll `1\n` und `0\n` mit 9600 Baud bleibt, Python 3.10, pyserial.

## Goals / Non-Goals

**Goals:**
- Nach jedem kontrollierten Ende und bei jedem Serial-Fehler ist abgeblendet.
- Eine hängende Verarbeitung führt innerhalb von etwa 0,5 s zu `0`, nicht erst nach dem Firmware-Timeout.
- Die Logik ist ohne Hardware testbar.

**Non-Goals:**
- Keine Änderung an Firmware oder Protokoll.
- Kein automatischer Neustart des Programms (Aufgabe eines Dienst-Managers).
- Keine Änderung der Entscheidungslogik (`multi-box-decision`) und des Standardgeräts (`gpu-required`).

## Decisions

### 1. Der Sender ist ein eigener Strang, die Pipeline setzt nur den Status

Ein `ActuatorLink` besitzt die serielle Schnittstelle und sendet in einem Hintergrund-Thread alle 0,2 s. Die Hauptschleife ruft nur `set_status(0|1)` auf. Das merkt sich Status und Zeitstempel. Ist der Zeitstempel beim Senden älter als 0,5 s, sendet der Thread `0` statt des gemerkten Status.

Zusätzlich weckt `set_status` den Sender sofort, damit das Abblenden nicht auf den Takt warten muss, und der Sender wacht zum Ablaufzeitpunkt der 0,5 s auf, sodass die `0` bei einem Hänger nach etwa 0,5 s kommt (gemessen 0,51 s) und nicht erst nach dem nächsten Takt.

*Warum:* Ein Sender in der Hauptschleife kann eine hängende Hauptschleife nicht erkennen. Ein getrennter Thread macht aus „keine neue Entscheidung" aktiv ein `0`. PyTorch gibt die GIL bei CUDA-Aufrufen frei, deshalb läuft der Thread auch während der Inferenz.

*Verworfen:* Weiter in der Hauptschleife senden und sich auf die Firmware verlassen. Das deckt den Hänger nur mit 1 bis 3 s Verzögerung ab. Ein einfacher Heartbeat-Thread, der den letzten Status wiederholt, ist die gefährlichste Variante: Er würde ein veraltetes `1` am Leben halten.

### 2. Wert 0,5 s für „veraltet", 0,2 s für den Sendetakt

0,5 s ist die Hälfte des kürzesten möglichen Firmware-Timeouts (1 s) und liegt über dem Dreifachen der größten gemessenen Frame-Dauer (0,16 s). 0,2 s Takt ergibt bis zu zwei bis drei Sendeversuche pro Staleness-Fenster.

### 3. Ein Beenden-Pfad für alles

Eine idempotente Funktion `shutdown()` setzt den Status auf 0, sendet `0\n`, leert den Puffer und schließt die Schnittstelle. Sie wird von den Handlern für SIGINT und SIGTERM, der Taste `c`, `sys.excepthook` und `atexit` aufgerufen. Das Schreiben hat ein Zeitlimit (`write_timeout` 0,5 s), damit ein hängender Adapter das Beenden nicht blockiert.

*Warum:* Im Legacy-Code gab es drei verschiedene Ausstiege mit eigener Aufräumlogik und keiner sendete `0`.

### 4. Wiederverbindung im Sender-Thread

Fällt das Schreiben aus, schließt der Thread die Schnittstelle und versucht alle 2 s, sie neu zu öffnen. Die Pipeline läuft unberührt weiter. Logs: ERROR beim Verlust, INFO bei Wiederherstellung, Erinnerung höchstens alle 30 s.

*Verworfen:* Wiederverbinden in der Hauptschleife. Ein hängendes `open()` würde die Erkennung blockieren.

### 5. Exit-Codes

Kontrolliertes Beenden (Strg-C, SIGTERM, `c`) endet mit 0, ein unbehandelter Fehler mit 1. So kann ein Dienst-Manager mit `Restart=on-failure` einen Absturz erkennen und einen gewollten Stopp unterscheiden.

### 6. Testbarkeit über ein Fake-Gerät

Die Tests nutzen ein Pseudo-Terminal (`pty.openpty()`) als Gegenstelle und lesen, was der Sender schreibt. Damit lassen sich Heartbeat, Hänger, SIGTERM, Adapter-Abriss und Wiederverbindung am Schreibtisch prüfen, ohne Mikrocontroller und GPU.

## Risks / Trade-offs

- **Frame dauert länger als 0,5 s (zum Beispiel erster CUDA-Frame, CPU-Betrieb)** → Der Sender schickt `0`, das Fernlicht flackert oder bleibt aus. Das ist die sichere Richtung. Gegenmaßnahme: Warm-up-Frame vor dem Freigeben, und CPU-Betrieb wird in `gpu-required` behandelt.
- **Signal-Handler läuft nicht, wenn die Hauptschleife in einem C-Aufruf feststeckt** → Deckt die Staleness-Regel aus Entscheidung 1 ab (nach etwa 0,5 s `0`), danach der Firmware-Timeout.
- **Sender-Thread stirbt unbemerkt** → Dann kommt nichts mehr an, und die Firmware blendet ab. Der Thread fängt Exceptions, loggt sie und startet seine Schleife neu.
- **Gerätename ändert sich nach dem Abziehen (`/dev/ttyUSB1`)** → Die Wiederverbindung findet das Gerät dann nicht. Gegenmaßnahme siehe Open Questions.
- **Firmware-Timeout ist nur als „1 bis 3 s" bekannt** → Die Design-Werte rechnen mit dem ungünstigen Ende (1 s). Ein genauer Wert würde die Margen nur verbessern.

## Migration Plan

1. Neuen Aktor-Code mit Tests am Schreibtisch (Pseudo-Terminal) validieren.
2. Auf `hba1` ohne Fahrzeug mit angeschlossenem Mikrocontroller prüfen: `kill -TERM` (Abschlusskommando), `kill -STOP` (friert den ganzen Prozess samt Sender ein, damit greift der Firmware-Timeout und lässt sich mit einer Stoppuhr messen) und Adapter ziehen und stecken. Den Hänger nur der Hauptschleife prüfen die automatisierten Tests mit einem Test-Hook.
3. Erst danach im Fahrzeug einsetzen.

Rollback: Das Legacy-Skript bleibt unverändert unter `legacy/` und auf `hba1` erhalten.

## Open Questions

- Soll eine udev-Regel einen festen Gerätenamen (zum Beispiel `/dev/hba-actuator`) für den CH341-Adapter vergeben? Das ändert die Specs nicht, macht die Wiederverbindung aber robuster.
- Wie lange ist der Firmware-Timeout genau? Ein Test mit `kill -STOP` und einer Stoppuhr am Relais würde das klären.
