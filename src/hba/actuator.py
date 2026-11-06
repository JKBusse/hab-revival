"""Aktor-Sender: schickt den Fernlicht-Status an den Mikrocontroller und fällt sicher aus.

`ActuatorLink` besitzt die serielle Schnittstelle. Die Hauptschleife ruft nur
`set_status(0|1)` auf und blockiert nie. Ein Hintergrund-Thread sendet:

* sofort nach jedem `set_status` (Abblenden darf nicht auf den Takt warten) und
* mindestens alle `tick` Sekunden (Heartbeat).

Fail-Safe-Regeln (Change `fail-safe-shutdown`):

* Ist die letzte Entscheidung älter als `stale_after`, wird `0` gesendet statt eines
  veralteten `1`. Eine hängende Hauptschleife blendet so nach etwa 0,5 s ab.
* Nach einem Verbindungs- oder Schreibfehler gilt `0`. Der Thread versucht alle
  `reconnect_every` Sekunden, die Verbindung neu aufzubauen.
* `close()` sendet `0\\n`, leert den Puffer und schließt. Es ist idempotent und dauert
  auch bei hängendem Adapter höchstens etwa 2 Sekunden.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable

PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT = 2  # Lese-Timeout der Schnittstelle
WRITE_TIMEOUT = 0.5

TICK_SECONDS = 0.2  # Heartbeat-Takt
STALE_SECONDS = 0.5  # ältere Entscheidungen gelten als veraltet
RECONNECT_SECONDS = 2.0
REMIND_SECONDS = 30.0
CLOSE_JOIN_SECONDS = 0.7  # 0,7 + 0,5 (Sperre) + 0,7 = 1,9 s im ungünstigsten Fall


def _open_serial(port: str, baudrate: int, write_timeout: float):
    import serial  # erst hier, damit das Modul ohne pyserial importierbar bleibt

    return serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=8,
        timeout=TIMEOUT,
        stopbits=serial.STOPBITS_ONE,
        write_timeout=write_timeout,
    )


class ActuatorLink:
    def __init__(
        self,
        port: str = PORT,
        baudrate: int = BAUDRATE,
        logger: logging.Logger | None = None,
        *,
        tick: float = TICK_SECONDS,
        stale_after: float = STALE_SECONDS,
        reconnect_every: float = RECONNECT_SECONDS,
        remind_every: float = REMIND_SECONDS,
        write_timeout: float = WRITE_TIMEOUT,
        serial_factory: Callable | None = None,
        clock: Callable[[], float] = time.monotonic,
        autostart: bool = True,
    ):
        self.port = port
        self.baudrate = baudrate
        self.logger = logger if logger is not None else logging.getLogger("HBA")
        self.tick = tick
        self.stale_after = stale_after
        self.reconnect_every = reconnect_every
        self.remind_every = remind_every
        self.write_timeout = write_timeout
        self._factory = serial_factory or (lambda: _open_serial(port, baudrate, write_timeout))
        self._clock = clock

        self._lock = threading.Lock()  # Status und Zeitstempel
        self._io_lock = threading.Lock()  # Zugriff auf die Schnittstelle
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._closed = False

        self._status = 0
        self._status_time = clock()
        self._serial = None
        self._lost = False  # Verlust wurde gemeldet, Wiederverbindung läuft
        self._last_attempt = clock()
        self._last_reminder = clock()

        self._open(initial=True)
        self._thread = threading.Thread(target=self._run, name="actuator-sender", daemon=True)
        if autostart:
            self._thread.start()

    # --- Schnittstelle für die Hauptschleife -------------------------------

    @property
    def connected(self) -> bool:
        return self._serial is not None

    def set_status(self, status: int) -> None:
        """Merkt sich die Entscheidung des aktuellen Frames. Blockiert nie."""
        with self._lock:
            if self._closed:
                return
            self._status = 1 if status == 1 else 0
            self._status_time = self._clock()
        self._wake.set()

    def close(self) -> None:
        """Sendet `0\\n`, leert den Puffer und schließt. Idempotent, höchstens etwa 2 s."""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._status = 0
        self._stop.set()
        self._wake.set()
        if self._thread.is_alive() and threading.current_thread() is not self._thread:
            self._thread.join(timeout=CLOSE_JOIN_SECONDS)

        got_lock = self._io_lock.acquire(timeout=self.write_timeout)
        try:
            serial_port, self._serial = self._serial, None
            if serial_port is not None:
                self._final_write(serial_port)
        finally:
            if got_lock:
                self._io_lock.release()

    # --- Sender-Thread ------------------------------------------------------

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._tick()
            except Exception:
                self.logger.exception("Aktor-Sender: unerwarteter Fehler, Schleife läuft weiter")
            self._wake.wait(self._next_wait())
            self._wake.clear()

    def _next_wait(self) -> float:
        """Wartezeit bis zum nächsten Durchlauf: der Takt, oder kürzer, wenn eine laufende `1`
        vorher veraltet. So kommt die `0` bei einem Hänger nach etwa 0,5 s, nicht erst nach
        dem nächsten Takt."""
        with self._lock:
            status, stamp = self._status, self._status_time
        remaining = stamp + self.stale_after - self._clock()
        if status == 1 and 0 < remaining < self.tick:
            return remaining + 0.005
        return self.tick

    def _tick(self) -> None:
        if self._closed:
            return
        now = self._clock()
        if self._serial is None:
            if now - self._last_attempt >= self.reconnect_every:
                self._last_attempt = now
                self._open(initial=False)
            if self._serial is None:
                return
        self._send(self._current_value(now))

    def _current_value(self, now: float) -> int:
        with self._lock:
            status, stamp = self._status, self._status_time
        return status if now - stamp <= self.stale_after else 0

    def _send(self, value: int) -> None:
        with self._io_lock:
            serial_port = self._serial
            if serial_port is None or self._closed:
                return
            try:
                serial_port.write(b"1\n" if value == 1 else b"0\n")
            except Exception as exc:
                self._on_lost(serial_port, exc)

    # --- Verbindung ---------------------------------------------------------

    def _open(self, initial: bool) -> None:
        try:
            self._serial = self._factory()
        except Exception as exc:
            self._serial = None
            now = self._clock()
            if initial:
                self._lost = True
                self.logger.error("configure_serial_connection: ERROR!")
                self._last_reminder = now
            elif now - self._last_reminder >= self.remind_every:
                self.logger.error("Serial connection still lost (%s): %s", self.port, exc)
                self._last_reminder = now
            return
        if initial:
            self.logger.info("configure_serial_connection: OK")
        elif self._lost:
            self.logger.info("Serial connection restored: %s", self.port)
        self._lost = False

    def _on_lost(self, serial_port, exc: Exception) -> None:
        try:
            serial_port.close()
        except Exception:
            pass
        self._serial = None
        self._lost = True
        now = self._clock()
        self._last_attempt = now
        self._last_reminder = now
        self.logger.error("Serial connection lost (%s): %s", self.port, exc)

    def _final_write(self, serial_port) -> None:
        def work():
            try:
                serial_port.write(b"0\n")
                serial_port.flush()
            except Exception as exc:
                self.logger.error("Abschlusskommando nicht gesendet: %s", exc)
            try:
                serial_port.close()
            except Exception:
                pass

        helper = threading.Thread(target=work, name="actuator-final-write", daemon=True)
        helper.start()
        helper.join(timeout=CLOSE_JOIN_SECONDS)
