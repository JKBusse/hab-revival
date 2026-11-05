"""Einfacher Serial-Aktor wie im Original (`legacy/yolov8.py`, Zeilen 88 bis 104 und 288 bis 307).

Legacy-Eigenheiten, die bewusst erhalten bleiben und im Change `fail-safe-shutdown`
ersetzt werden:

* In jedem Frame wird ein Kommando geschrieben (`1\\n` oder `0\\n`), ohne Heartbeat.
* Nach einem Schreibfehler ist der Aktor dauerhaft aus, ohne Wiederverbindung.
* `close()` sendet kein Abschlusskommando.

Der Aktor blockiert nur so lange wie ein Schreibvorgang.
"""

from __future__ import annotations

import logging

PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT = 2


class SerialActuator:
    def __init__(self, port: str = PORT, baudrate: int = BAUDRATE, logger: logging.Logger | None = None):
        self.port = port
        self.enabled = False
        self._serial = None
        try:
            import serial  # erst hier, damit das Modul ohne pyserial importierbar bleibt

            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=8,
                timeout=TIMEOUT,
                stopbits=serial.STOPBITS_ONE,
            )
            self.enabled = True
        except Exception:
            print("Serial connection not possible")
        if logger is not None:
            if self.enabled:
                logger.info("configure_serial_connection: OK")
            else:
                logger.error("configure_serial_connection: ERROR!")

    def set_status(self, status: int) -> None:
        if not self.enabled:
            return
        try:
            self._serial.write(b"1\n" if status == 1 else b"0\n")
        except Exception:
            self.enabled = False
            print("Serial not Possible!")

    def close(self) -> None:
        # Legacy: kein Abschlusskommando (siehe fail-safe-shutdown).
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
