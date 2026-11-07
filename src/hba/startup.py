"""Start-Prüfung der GPU (Change `gpu-required`).

Ablauf: CUDA verfügbar (beim Erzeugen des Detektors), Modell geladen, Warm-up-Frame innerhalb
von 30 Sekunden. Scheitert ein Schritt, wird ein ERROR geloggt, `0` gesendet und mit
Exit-Code 3 beendet. Eine Kamera, die beim Warm-up kein Bild liefert, ist kein GPU-Problem
(Exit-Code 1). Einen CPU-Fallback gibt es nicht.
"""

from __future__ import annotations

import logging
from typing import Callable

from hba import exit_codes
from hba.app import WARMUP_SECONDS, Pipeline, WarmUpTimeout
from hba.capture import CameraError
from hba.detect import GpuUnavailable
from hba.lifecycle import Lifecycle


def create_detector_or_exit(factory: Callable, lifecycle: Lifecycle, logger: logging.Logger):
    """Erzeugt den Detektor. Ohne nutzbare GPU: ERROR, `0`, Exit-Code 3."""
    try:
        return factory()
    except GpuUnavailable as exc:
        logger.error("Keine nutzbare GPU: %s", exc)
        lifecycle.end(exit_codes.EXIT_NO_GPU)


def warm_up_or_exit(
    pipeline: Pipeline,
    lifecycle: Lifecycle,
    logger: logging.Logger,
    gpu: bool,
    timeout: float = WARMUP_SECONDS,
) -> None:
    """Warm-up-Frame mit Zeitlimit. Auf der GPU gilt jeder Fehlschlag als „keine nutzbare GPU"."""
    try:
        pipeline.warm_up(timeout=timeout)
    except WarmUpTimeout as exc:
        # Der Thread hängt in einem CUDA-Aufruf: nicht darauf warten.
        lifecycle.hard_exit(exit_codes.EXIT_NO_GPU, f"Keine nutzbare GPU: {exc}")
    except CameraError as exc:
        # Kein GPU-Problem: eigene Meldung, Laufzeitfehler (Exit-Code 1), der Dienst-Manager startet neu.
        logger.error("Kamera beim Warm-up nicht lesbar: %s", exc)
        lifecycle.end(exit_codes.EXIT_ERROR)
    except GpuUnavailable as exc:
        logger.error("Keine nutzbare GPU: %s", exc)
        lifecycle.end(exit_codes.EXIT_NO_GPU)
    except Exception as exc:
        if not gpu:
            raise
        logger.error("Keine nutzbare GPU: Warm-up fehlgeschlagen (%s)", exc)
        lifecycle.end(exit_codes.EXIT_NO_GPU)
