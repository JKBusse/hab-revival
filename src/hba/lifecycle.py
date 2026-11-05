"""Minimaler Lebenszyklus wie im Original (`legacy/yolov8.py`, Zeilen 37 bis 54).

Legacy-Eigenheiten, die im Change `fail-safe-shutdown` ersetzt werden:

* Unbehandelte Fehler und Strg-C beenden mit Exit-Code 0.
* Beim Beenden wird kein abschließendes Kommando an den Aktor gesendet.
"""

from __future__ import annotations

import logging
import signal
import sys
from typing import Callable

from hba import monitor


class Lifecycle:
    def __init__(self, logger: logging.Logger, close_windows: Callable[[], None] | None = None):
        self.logger = logger
        self._close_windows = close_windows if close_windows is not None else _destroy_windows

    def install(self) -> None:
        sys.excepthook = self._on_unhandled_exception
        signal.signal(signal.SIGINT, self._on_sigint)

    def end(self) -> None:
        print("---END---")
        self._close_windows()
        monitor.log_end(self.logger)
        sys.exit(0)

    def _on_unhandled_exception(self, exc_type, exc_value, exc_traceback) -> None:
        print("Unhandled exception:", exc_type, exc_value)
        self.logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        self.end()

    def _on_sigint(self, signum, frame) -> None:
        self.logger.info("Manual end CTR-C")
        self.end()


def _destroy_windows() -> None:
    import cv2

    cv2.destroyAllWindows()
