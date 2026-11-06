"""Datensammlung: Ausschnitte, Zufalls-Stichproben und Detektionsbeispiele mit Auto-Label.

Verhalten wie im Legacy-Skript `legacy/yolov8.py` (Zeilen 79 bis 86, 158 bis 173, 187 bis 193,
239 bis 243). Bekannte Eigenheiten bleiben erhalten (siehe Baseline-Spec `data-collection`):

* Zufallsbilder und Detektionsbeispiele werden auch ohne `-s` geschrieben.
* Das Label enthält nur die ERSTE Box, das Detektionsbild zeigt keine Boxen.
* Ordner werden nicht angelegt. Fehlt einer oder schlägt ein Schreibvorgang fehl, gibt es ein
  WARNING und die betroffene Aufnahme (`crop`, `random`, `detection`) entfällt für den Rest des
  Laufs. Die Erkennung läuft weiter (Change `systemd-service`).

Zeit und Zufall werden eingespeist (`name`, `rng` mit `random()`), damit Tests deterministisch sind.
"""

from __future__ import annotations

import glob
import logging
import os
import random
from typing import Sequence

import cv2

from hba.ports import Box

from hba.config import DEFAULTS, RecordingConfig

MAX_FILES = DEFAULTS["recording"]["max_files"]
# Standardwahrscheinlichkeiten wie im Original: randrange(1, 100) == 42 (1 von 99 Frames) und
# randrange(1, 100) > 90 (9 von 99 Frames mit Detektion). Statt ganzer Zufallszahlen gelten
# jetzt Wahrscheinlichkeiten (`rng.random() < p`), damit sie konfigurierbar sind.
SAMPLE_PROBABILITY = DEFAULTS["recording"]["sample_probability"]
DETECTION_PROBABILITY = DEFAULTS["recording"]["detection_probability"]


def timestamp_name(seconds: float) -> str:
    """Dateiname aus dem Zeitstempel ohne Punkt, wie `str(time.time()).replace(".", "")`."""
    return str(seconds).replace(".", "")


def max_files(folder_path: str, max_files: int = MAX_FILES) -> None:
    """Löscht die ältesten Dateien (nach Änderungszeit), bis höchstens `max_files` übrig sind."""
    files = glob.glob(os.path.join(folder_path, "*"))
    if len(files) > max_files:
        files.sort(key=os.path.getmtime)
        for path in files[: len(files) - max_files]:
            os.remove(path)
            print(f"Deleted file: {path}")


def _write_image(path: str, image) -> None:
    # cv2.imwrite meldet einen fehlenden Ordner nur über den Rückgabewert.
    if not cv2.imwrite(path, image):
        raise OSError(f"Bild konnte nicht geschrieben werden: {path}")


def label_line(cls: int, box: Box) -> str:
    """YOLO-Zeile der ersten Box, normiert durch 640, wie `make_label` im Original.

    Das Original rundet die Ecke (`cords`) und rechnet die Größe aus den ungerundeten Werten.
    """
    leng = box.x2 - box.x1
    hig = box.y2 - box.y1
    x_center = (round(box.x1) + (leng / 2)) / 640
    y_center = (round(box.y1) + (hig / 2)) / 640
    return f"{int(cls)} {x_center} {y_center} {leng / 640} {hig / 640}"


class Recorder:
    def __init__(
        self,
        base_path: str,
        save_all: bool,
        rng: random.Random,
        max_files_per_folder: int = MAX_FILES,
        sample_probability: float = SAMPLE_PROBABILITY,
        detection_probability: float = DETECTION_PROBABILITY,
        logger: logging.Logger | None = None,
    ):
        self.base_path = base_path
        self.save_all = save_all
        self.rng = rng
        self.max_files_per_folder = max_files_per_folder
        self.sample_probability = sample_probability
        self.detection_probability = detection_probability
        self.logger = logger if logger is not None else logging.getLogger("HBA")
        self.disabled: set[str] = set()

    def disable_all(self, reason: str = "") -> None:
        """Schaltet alle Aufnahmen ab (Ablage nicht verfügbar). Der Aufrufer meldet den Grund."""
        self.disabled.update({"crop", "random", "detection"})

    def _guarded(self, category: str, action) -> None:
        """Führt eine Aufnahme aus. Schreibfehler schalten nur diese Aufnahme ab, mit einem WARNING."""
        if category in self.disabled:
            return
        try:
            action()
        except OSError as exc:
            self.disabled.add(category)
            self.logger.warning("Aufnahme '%s' abgeschaltet, Erkennung läuft weiter: %s", category, exc)

    @classmethod
    def from_config(
        cls, recording: RecordingConfig, save_all: bool, rng: random.Random, logger: logging.Logger | None = None
    ) -> "Recorder":
        return cls(
            recording.path,
            save_all,
            rng,
            max_files_per_folder=recording.max_files,
            sample_probability=recording.sample_probability,
            detection_probability=recording.detection_probability,
            logger=logger,
        )

    def _path(self, *parts: str) -> str:
        return os.path.join(self.base_path, *parts)

    def record_frame(self, name: str, crop) -> None:
        """Schritt vor der Erkennung: `-s` und die Stichprobe (Ausschnitt 960x426)."""
        if self.save_all:
            self._guarded("crop", lambda: _write_image(self._path("images", "crop", name + ".png"), crop))
        if self.rng.random() < self.sample_probability:  # Zufallszahl immer ziehen, auch bei abgeschalteter Aufnahme

            def sample():
                _write_image(self._path("images", "random", name + ".png"), crop)
                max_files(self._path("images", "random"), self.max_files_per_folder)

            self._guarded("random", sample)

    def record_detection(self, name: str, model_input, boxes: Sequence[Box]) -> None:
        """Schritt nach der Erkennung: in einem Teil der Frames mit Boxen Bild und Label der ersten Box."""
        if len(boxes) == 0:
            return
        if self.rng.random() < self.detection_probability:

            def example():
                _write_image(self._path("images", "detections", name + ".png"), model_input)
                with open(self._path("labels", "detections", name + ".txt"), "w") as handle:
                    handle.write(label_line(boxes[0].cls, boxes[0]))
                max_files(self._path("images", "detections"), self.max_files_per_folder)
                max_files(self._path("labels", "detections"), self.max_files_per_folder)

            self._guarded("detection", example)
