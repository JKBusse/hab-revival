"""Monitoring: Logdatei im Legacy-Format, Boxdarstellung und Stream-Dateien.

Meldungstexte und Reihenfolge wie in `legacy/yolov8.py`, damit vorhandene Auswertungen
(zum Beispiel der Replay in `multi-box-decision`) weiter funktionieren.
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import replace
from typing import Sequence

import cv2

from hba.ports import Box
from hba.config import RelevanceConfig
from hba.relevance import MAX_WIDTH, legacy_area_result

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGER_NAME = "HBA"

YELLOW = (0, 255, 255)  # BGR
RED = (0, 0, 255)
WHITE = (255, 255, 255)
MARGIN = 13  # Abstand der Box zur Detektion in Pixeln


# Meldungen, die in jedem Frame entstehen: stehen in der Datei, nicht im Journal (sonst Flut).
_FRAME_CHATTER = (
    "-Frame START-", "Detections:", "cord0:", "Len:", "In active area", "No usefull detection",
    "HBA Status:", "DIFF:",
)


class _JournalFilter(logging.Filter):
    """Für stderr (Journal): Warnungen und Fehler immer, Infos nur ohne Frame-Takt."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.WARNING or not record.getMessage().startswith(_FRAME_CHATTER)


class SafeFileHandler(logging.FileHandler):
    """Datei-Log, das sich bei einem Schreibfehler (zum Beispiel Stick gezogen) einmal meldet und
    abschaltet, statt bei jeder Meldung einen Traceback zu erzeugen. Das Programm läuft weiter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed = False

    def emit(self, record) -> None:
        if not self.failed:
            super().emit(record)

    def handleError(self, record) -> None:
        if not self.failed:
            self.failed = True
            sys.stderr.write("WARNUNG: Datei-Log abgeschaltet (Schreibfehler), Meldungen nur noch im Journal\n")


def setup_logger(log_dir: str, start_name: str, stream=None) -> logging.Logger:
    """Schreibt nach `<log_dir>/<start_name>.log` mit Stufe DEBUG und zusätzlich nach stderr (Journal).

    Fehlt der Ordner oder ist er nicht beschreibbar, läuft das Programm trotzdem: ein WARNING nennt
    den Pfad, und die Meldungen gehen nur nach stderr. Mehrfacher Aufruf hängt keine doppelten
    Handler an.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    formatter = logging.Formatter(LOG_FORMAT)

    journal = logging.StreamHandler(stream if stream is not None else sys.stderr)
    journal.setLevel(logging.INFO)
    journal.addFilter(_JournalFilter())
    journal.setFormatter(formatter)
    logger.addHandler(journal)

    path = os.path.join(log_dir, start_name + ".log")
    try:
        handler = SafeFileHandler(path)
    except OSError as exc:
        logger.warning("Ablage nicht verfügbar: Datei-Log aus (%s): %s", log_dir, exc)
    else:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def file_logging_active(logger: logging.Logger) -> bool:
    return any(isinstance(h, SafeFileHandler) and not h.failed for h in logger.handlers)


def check_storage(path: str, logger: logging.Logger) -> bool:
    """Prüft den Ablagepfad. Fehlt er, gibt es ein WARNING und die Aufnahmen bleiben aus."""
    if os.path.isdir(path) and os.access(path, os.W_OK):
        return True
    logger.warning("Ablage nicht verfügbar: %s existiert nicht oder ist nicht beschreibbar, Aufnahmen aus", path)
    return False


def log_start(logger: logging.Logger, start_name: str, args_repr: str) -> None:
    logger.critical("---START---")
    logger.info("Start Time: {}".format(start_name))
    logger.info("Arguments: {}".format(args_repr))


def log_config(logger: logging.Logger, loaded) -> None:
    """Die effektiven Werte mit ihrer Quelle (Flag, Datei, Standard) und Warnungen."""
    from hba.config import describe

    logger.info("Konfigurationsdatei: %s", loaded.path if loaded.path else "keine (nur Standardwerte)")
    for line in describe(loaded):
        logger.info(line)
    for warning in loaded.warnings:
        logger.warning(warning)


def log_end(logger: logging.Logger) -> None:
    logger.critical("---END---\n")


def log_frame_start(logger: logging.Logger) -> None:
    logger.info("-Frame START-")


def _log_area(logger: logging.Logger, box: Box, relevance: RelevanceConfig | None = None):
    """Entspricht dem Logteil von `get_active_area` und liefert dessen Ergebnis."""
    logger.info("cord0: {} cord1: {} cord2: {} cord3: {}".format(box.x1, box.y1, box.x2, box.y2))
    logger.info("Len: {} Hei: {}".format(box.width, box.top))
    return legacy_area_result(box, relevance)


def log_boxes(logger: logging.Logger, boxes: Sequence[Box], relevance: RelevanceConfig | None = None) -> None:
    """Detektionsanzahl und Bewertung jeder Box."""
    logger.info("Detections: {}".format(len(boxes)))
    if len(boxes) == 0:
        return
    for index, box in enumerate(boxes):
        result = _log_area(logger, box, relevance)
        logger.info("In active area {} : {}".format(index, result))
    if boxes[0].width >= (relevance.max_width if relevance else MAX_WIDTH):
        logger.info("No usefull detection")


def log_status(logger: logging.Logger, status: int) -> None:
    logger.info("HBA Status: {}".format(status))


def log_frame_duration(logger: logging.Logger, seconds: float) -> None:
    logger.info("DIFF: " + str(round(seconds, 4)))


def annotate(image, boxes: Sequence[Box], logger: logging.Logger | None = None, relevance: RelevanceConfig | None = None):
    """Zeichnet die Boxen auf eine Kopie des Bilds.

    gelb  Breite < 500, aber obere Kante <= 160 (Ergebnis `None`)
    rot   Klasse 0 (back)
    weiß  Klasse 1 (front)
    Wie im Original wird die Bewertung auf den gerundeten Koordinaten berechnet.
    """
    out = image.copy()
    for box in boxes:
        rounded = replace(box, x1=round(box.x1), y1=round(box.y1), x2=round(box.x2), y2=round(box.y2))
        if logger is not None:
            result = _log_area(logger, rounded, relevance)
        else:
            result = legacy_area_result(rounded, relevance)
        if result is None:
            box_color, text_color = YELLOW, RED
        elif int(box.cls) == 0:
            box_color, text_color = RED, RED
        else:
            box_color, text_color = WHITE, WHITE
        cv2.rectangle(
            out,
            (rounded.x1 - MARGIN, rounded.y1 - MARGIN),
            (rounded.x2 + MARGIN, rounded.y2 + MARGIN),
            box_color,
            3,
        )
        cv2.putText(
            out,
            str(float(box.cls)).replace(".0", ""),
            (rounded.x2 + 20, rounded.y2 + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            text_color,
            1,
            cv2.LINE_AA,
        )
    return out


def write_stream_frame(image, seconds: float, directory: str = "/tmp") -> str:
    """Schreibt das annotierte Bild als `<directory>/<zeitstempel>.png` und liefert den Pfad."""
    path = os.path.join(directory, str(seconds).replace(".", "") + ".png")
    if not cv2.imwrite(path, image):
        raise OSError(f"Stream-Bild konnte nicht geschrieben werden: {path}")
    return path
