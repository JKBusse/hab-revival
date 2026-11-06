# Fail-Safe: Wie das Fernlicht ausfällt

Das Relais ist als **Freigabe in Reihe** mit dem Lichthebel verbaut. Der Assistent kann Fernlicht
nur erlauben oder sperren. Jeder Ausfall bedeutet also Abblendlicht. Dieses Dokument beschreibt,
welche Absicherungen es zusätzlich gibt, damit auch ein hängendes oder beendetes Programm schnell
und eindeutig abblendet.

Code: `src/hba/actuator.py` (`ActuatorLink`), `src/hba/lifecycle.py`, `src/hba/app.py`.

## Drei Absicherungen

```
Hauptschleife --set_status(0|1)--> ActuatorLink --Sender-Thread--> /dev/ttyUSB0 --> Mikrocontroller
                                     |  sofort nach set_status, mindestens alle 0,2 s
                                     |  Entscheidung aelter als 0,5 s  ->  sendet 0
                                     |  Verbindung weg                 ->  Status 0, Wiederverbindung alle 2 s
                                     v
                                  close(): sendet 0, leert, schliesst (idempotent, <= 2 s)

Firmware: blendet nach 1 bis 3 s ohne Kommando selbst ab (Messung steht aus, siehe unten)
```

| Schicht | Wirkt bei | Zeit bis `0` |
|---|---|---|
| Staleness im Sender | hängende Hauptschleife (CUDA, Kamera) | etwa 0,5 s |
| Abschlusskommando | kontrolliertes Ende, Exception | sofort beim Beenden |
| Firmware-Timeout | SIGKILL, Absturz, Stromausfall des Rechners, Adapter weg | 1 bis 3 s |

## Pfade und Szenarien

Jedes Szenario der Delta-Specs `actuator-control` und `runtime-configuration` des Changes
`fail-safe-shutdown` ist einem Pfad und einem Test zugeordnet.

| Szenario | Pfad | Test |
|---|---|---|
| Adapter vorhanden | `ActuatorLink.__init__` öffnet die Schnittstelle, loggt `configure_serial_connection: OK` | `test_ok_is_logged_when_adapter_present` |
| Adapter fehlt beim Start | Konstruktor wirft nicht, loggt `configure_serial_connection: ERROR!`, Status 0, Thread verbindet später | `test_start_without_adapter_does_not_raise_and_connects_when_device_appears` |
| Normalbetrieb | Sender wird von `set_status` geweckt, Heartbeat alle 0,2 s | `test_status_arrives_and_gaps_stay_below_half_a_second` |
| Verarbeitung hängt | Staleness: `_current_value` liefert nach 0,5 s `0`, Sender wacht zum Ablaufzeitpunkt auf | `test_stale_decision_sends_zero_and_never_one_again`, `test_hanging_main_loop_dims_within_700_ms` |
| Adapter wird abgezogen und wieder eingesteckt | Schreibfehler, `_on_lost`, Versuch alle 2 s in `_tick`, INFO bei Wiederherstellung | `test_reconnect_after_adapter_is_unplugged_and_replugged` |
| Adapter bleibt weg | ERROR einmal beim Verlust, Erinnerung höchstens alle 30 s, Status 0 | `test_error_is_logged_once_with_reminders_every_30_seconds` |
| Beenden bei eingeschaltetem Fernlicht | `Lifecycle.shutdown` ruft `ActuatorLink.close`, das `0\n` sendet | `test_controlled_end_sends_zero_and_exits_with_code_0` (Strg-C) |
| Beenden per SIGTERM | SIGTERM-Handler ruft `Lifecycle.end(0)` | `test_controlled_end_sends_zero_and_exits_with_code_0` (SIGTERM) |
| Adapter beim Beenden nicht verfügbar | `close` begrenzt Join und Schreiben (zusammen höchstens etwa 1,9 s) | `test_close_with_hanging_adapter_takes_at_most_two_seconds`, `test_shutdown_with_blocking_port_takes_at_most_two_seconds` |
| Unerwarteter Fehler | `sys.excepthook` loggt, ruft `Lifecycle.end(1)`: `0\n`, `---END---`, Exit-Code 1 | `test_unhandled_exception_sends_zero_and_exits_with_nonzero_code` |
| SIGTERM von einem Dienst-Manager | siehe oben, Exit-Code 0 | `test_controlled_end_sends_zero_and_exits_with_code_0` |
| SIGKILL | kein Handler möglich, es greift der Firmware-Timeout | nicht automatisiert, Messung in Aufgabe 5.2 |

Zusätzlich: Die Taste `c` endet über `Lifecycle.end(0)` (Test mit `life.end()`), ein normales
Interpreter-Ende über `atexit` (`test_normal_interpreter_exit_also_sends_zero`).

## Firmware-Timeout

Der Mikrocontroller blendet nach **1 bis 3 Sekunden** ohne Kommando selbst ab. Der genaue Wert ist
unbekannt. Die Werte im Code rechnen mit dem ungünstigen Ende (1 s): Staleness 0,5 s, Takt 0,2 s.

**Messverfahren** (Aufgabe 5.2, benötigt den Mikrocontroller):

1. Programm mit Pseudo-Status `1` laufen lassen, Fernlicht-Relais ist angezogen.
2. `kill -STOP <pid>` friert den ganzen Prozess samt Sender-Thread ein, es kommt nichts mehr an.
3. Stoppuhr starten und die Zeit bis zum Abfallen des Relais messen. Dreimal wiederholen.
4. `kill -CONT <pid>` oder Prozess beenden.

Ergebnis: **noch nicht gemessen.**

## Grenzen

- Ein Hänger im C-Code hält Signal-Handler an. Dann greift die Staleness (der Sender-Thread läuft, weil
  PyTorch die GIL bei CUDA-Aufrufen freigibt) und notfalls die Firmware.
- Wechselt der Adapter nach dem Abziehen den Gerätenamen (`/dev/ttyUSB1`), findet die
  Wiederverbindung ihn nicht. Abhilfe wäre eine udev-Regel mit festem Namen (offen im Design).
