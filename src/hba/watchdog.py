"""Watchdog für die Hauptschleife (Change `gpu-required`).

Auf `hba1` kann die GPU unter Last vom PCIe-Bus fallen (Xid 79). Ein CUDA-Aufruf kehrt dann
unter Umständen nie zurück, statt einen Fehler zu melden. Die Hauptschleife meldet jeden fertigen
Frame mit `beat()`. Vergeht länger als `timeout` Sekunden ohne Meldung, ruft der Watchdog einmal
`on_expire` auf. Im Betrieb beendet das den Prozess hart mit Exit-Code 4, damit der
Dienst-Manager neu startet. Bis dahin hält die Staleness-Regel des Aktors das Licht abgeblendet.
"""

from __future__ import annotations

import threading
import time
from typing import Callable

WATCHDOG_SECONDS = 5.0
POLL_SECONDS = 0.1


class Watchdog:
    def __init__(
        self,
        on_expire: Callable[[], None],
        timeout: float = WATCHDOG_SECONDS,
        poll: float = POLL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.on_expire = on_expire
        self.timeout = timeout
        self.poll = poll
        self._clock = clock
        self._last_beat = clock()
        self._fired = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def beat(self) -> None:
        self._last_beat = self._clock()

    def start(self) -> None:
        """Startet die Überwachung. Der Zähler beginnt jetzt, nicht bei der Erzeugung."""
        self.beat()
        self._thread = threading.Thread(target=self._run, name="watchdog", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def check(self) -> bool:
        """Prüft einmal. Liefert True, wenn der Watchdog dabei ausgelöst hat (höchstens einmal)."""
        if self._fired or self._clock() - self._last_beat < self.timeout:
            return False
        self._fired = True
        self.on_expire()
        return True

    def _run(self) -> None:
        while not self._stop.wait(self.poll):
            if self.check():
                return
