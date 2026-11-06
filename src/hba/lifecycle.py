"""Lebenszyklus: kontrolliertes Beenden mit Abschlusskommando (Change `fail-safe-shutdown`).

Alle Ausstiege laufen über `shutdown()`: Strg-C, SIGTERM, die Taste `c` (über `end()`),
unbehandelte Exceptions und `atexit`. `shutdown()` sendet `0\\n` an den Aktor, leert den
Puffer und schließt die Schnittstelle. Es ist idempotent.

Exit-Codes: kontrolliertes Ende (Strg-C, SIGTERM, `c`) endet mit 0, ein unbehandelter
Fehler mit 1. Ein Dienst-Manager kann so einen Absturz von einem gewollten Stopp
unterscheiden.
"""

from __future__ import annotations

import atexit
import logging
import os
import signal
import sys
import threading
import time
from typing import Callable

from hba import exit_codes, monitor
from hba.ports import Actuator


class Lifecycle:
    def __init__(
        self,
        logger: logging.Logger,
        actuator: Actuator | None = None,
        close_windows: Callable[[], None] | None = None,
        hard_exit_fn: Callable[[int], None] = os._exit,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.logger = logger
        self.actuator = actuator
        self._close_windows = close_windows if close_windows is not None else _destroy_windows
        self._hard_exit_fn = hard_exit_fn
        self._sleep = sleep
        self._shutdown_lock = threading.Lock()
        self._shut_down = False

    def install(self) -> None:
        sys.excepthook = self._on_unhandled_exception
        signal.signal(signal.SIGINT, self._on_sigint)
        signal.signal(signal.SIGTERM, self._on_sigterm)
        atexit.register(self.shutdown)

    def shutdown(self) -> None:
        """Blendet ab und gibt die Schnittstelle frei. Idempotent."""
        with self._shutdown_lock:
            if self._shut_down:
                return
            self._shut_down = True
        if self.actuator is not None:
            try:
                self.actuator.close()
            except Exception:
                self.logger.exception("Abschlusskommando fehlgeschlagen")

    def end(self, code: int = exit_codes.EXIT_OK) -> None:
        print("---END---")
        self.shutdown()
        self._close_windows()
        monitor.log_end(self.logger)
        sys.exit(code)

    def hard_exit(self, code: int, reason: str) -> None:
        """Beendet sofort, ohne auf hängende Threads zu warten (Watchdog, hängender Warm-up).

        Setzt zuerst `0` (der Sender schickt es sofort, ohne zu blockieren), wartet kurz,
        schreibt das Log fertig und beendet dann mit `os._exit`.
        """
        self.logger.error("%s (Exit-Code %d)", reason, code)
        print("---END---")
        if self.actuator is not None:
            try:
                self.actuator.set_status(0)
            except Exception:
                pass
            self._sleep(0.15)
        monitor.log_end(self.logger)
        for handler in self.logger.handlers:
            try:
                handler.flush()
            except Exception:
                pass
        self._hard_exit_fn(code)

    def _on_unhandled_exception(self, exc_type, exc_value, exc_traceback) -> None:
        print("Unhandled exception:", exc_type, exc_value)
        self.logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        self.end(exit_codes.EXIT_ERROR)

    def _on_sigint(self, signum, frame) -> None:
        self.logger.info("Manual end CTR-C")
        self.end(exit_codes.EXIT_OK)

    def _on_sigterm(self, signum, frame) -> None:
        self.logger.info("Manual end SIGTERM")
        self.end(exit_codes.EXIT_OK)


def _destroy_windows() -> None:
    import cv2

    cv2.destroyAllWindows()
