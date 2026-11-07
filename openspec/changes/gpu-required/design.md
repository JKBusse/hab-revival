# Design

## Context

Motivation steht in `proposal.md`. Auf `hba1` wird die GPU beim Boot nicht immer erkannt und kann unter Last vom PCIe-Bus fallen (Xid 79). Dabei gibt es zwei Ausfallarten: einen **Fehler** (die Inferenz wirft eine Exception) und einen **Hänger** (ein CUDA-Aufruf kehrt nie zurück). Das Relais gibt nur frei (Freigabe in Reihe), ein Ausfall bedeutet Abblendlicht. Sicher ist beides, kritisch ist die Verfügbarkeit.

Voraussetzungen: `fail-safe-shutdown` (Sender-Thread, `shutdown()`, Exit-Code 1) und `modular-pipeline` (Detektor-Port).

## Goals / Non-Goals

**Goals:**
- Ohne nutzbare GPU startet die Pipeline nie, auch nicht langsam auf der CPU.
- Fehler und Hänger führen zum Abblenden und zu einem Prozessende, damit der Dienst neu startet.
- Alles lässt sich auf dem Mac mit Fakes testen.

**Non-Goals:**
- Kein CPU-Fallback, kein CUDA-Reinit im selben Prozess, keine Behebung der Hardwareprobleme, kein Boot-Rescan.

## Decisions

### 1. Start-Prüfung in drei Stufen mit Zeitlimit

CUDA verfügbar, Modell auf der GPU geladen, Warm-up-Frame fertig, jeweils vor der Hauptschleife. Das Zeitlimit für den Warm-up beträgt 30 s, weil der erste CUDA-Frame deutlich länger dauert als spätere (cuDNN-Initialisierung). Der Warm-up ist schon in `fail-safe-shutdown` als Gegenmaßnahme gegen eine Staleness-Verletzung vorgesehen und wird hier zur Pflicht.

*Alternative:* nur `torch.cuda.is_available()`. Verworfen, weil das auch dann wahr sein kann, wenn die GPU beim ersten echten Aufruf abstürzt.

### 2. Watchdog als eigener Thread mit hartem Abbruch

Die Hauptschleife meldet nach jedem fertigen Frame einen Zeitstempel. Der Watchdog prüft jede Sekunde, ob er älter als 5 s ist. Dann versucht er `0` zu senden (der Sender-Thread tut das ohnehin über die Staleness-Regel), loggt und ruft `os._exit(4)` auf. Ein normales `sys.exit` würde auf die hängende Hauptschleife warten oder in atexit-Handlern blockieren.

5 s entsprechen dem rund 50-Fachen der gemessenen Median-Dauer (0,1 s) und dem rund 30-Fachen des Maximums (0,16 s). Ein Fehlalarm ist unwahrscheinlich, die Ausfallzeit nach einem Hänger bleibt kurz.

*Verworfen:* systemd-Watchdog (`WatchdogSec`) als alleinige Lösung. Er lässt sich nicht auf dem Mac testen und hängt vom Dienst ab. Er kann später ergänzend dazukommen.

### 3. Exit-Codes als feste Tabelle

0 Stopp, 1 Laufzeitfehler, 2 Konfiguration (aus `config-file`), 3 keine GPU, 4 Watchdog. Der Dienst-Manager kann damit Restart-Verhalten unterscheiden (zum Beispiel längere Wartezeit bei 3). Die Tabelle liegt an einer Stelle im Code und in der Spec.

### 4. Kein CPU-Fallback

Auf dem i3-5010U dauert ein Frame mehrere Sekunden. Die Staleness-Regel würde fast immer `0` erzwingen, das System liefe scheinbar, wäre aber nutzlos. Ein klares Beenden meldet den Zustand besser.

### 5. CPU bleibt für Entwicklung

`-d cpu` ist weiterhin erlaubt (Mac), loggt aber ein WARNING. Der Watchdog-Grenzwert ist dann zu knapp. Er bleibt aber unverändert, weil die CPU im Betrieb nicht vorgesehen ist. In Tests ersetzt ein Fake-Detektor das Modell, sodass das nicht stört.

### 6. Testbarkeit

Fake-Detektoren simulieren „wirft Exception", „hängt" (blockiert auf einem Event) und „langsam". Der Watchdog bekommt eine einspeisbare Uhr und eine einspeisbare Abbruchfunktion (im Test statt `os._exit`). Ein Subprozess-Test prüft den echten Exit-Code 4.

## Risks / Trade-offs

- **Fehlalarm durch einen langen Frame (zum Beispiel Throttling)** → Neustart kostet einige Sekunden Abblendlicht, das ist die sichere Richtung. Das Log zeigt Frame-Dauern, damit sich die Grenze nachjustieren lässt.
- **Neustart-Schleife bei dauerhaftem GPU-Ausfall** → Begrenzung der Neustart-Rate liegt in `systemd-service`. Bis dahin gibt es kein Dauer-Neustarten ohne Dienst.
- **`os._exit` überspringt Aufräumen** → Gewollt. Das Abblenden übernimmt der Sender-Thread beziehungsweise der Firmware-Timeout von 1 bis 3 s.
- **Warm-up verzögert den Start** → Einige Sekunden, bei Dienststart unkritisch (zuerst bleibt ohnehin abgeblendet).
- **Die GPU ist beim Boot nicht da** → Der Dienst startet neu, bis sie erkannt wird. Ein Rescan ist nicht im Umfang.

## Migration Plan

1. Start-Prüfung und Exit-Codes auf dem Mac mit Fakes testen.
2. Auf `hba1` mit echter GPU prüfen (Warm-up-Dauer messen), danach mit `CUDA_VISIBLE_DEVICES=` ohne GPU starten und Exit-Code 3 prüfen.
3. Watchdog-Hänger auf `hba1` über einen Test-Schalter im Detektor simulieren (kein `SIGSTOP`, das würde auch den Watchdog-Thread anhalten) und Exit-Code 4 prüfen.

Rollback: `-d cpu` stellt das bisherige Verhalten her.

## Open Questions

- Gemessene Warm-up-Dauer auf `hba1` (2026-11-07, P106-100, drei Läufe mit frischem Prozess): 6,6 s, 3,9 s, 3,5 s. Die Grenze von 30 s hat reichlich Abstand und bleibt.
