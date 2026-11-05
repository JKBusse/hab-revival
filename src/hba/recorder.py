"""Datensammlung: Ausschnitte, Zufalls-Stichproben und Detektionsbeispiele mit Auto-Label.

Verhalten wie im Legacy-Skript `legacy/yolov8.py` (Zeilen 79 bis 86, 158 bis 173, 187 bis 193,
239 bis 243). Bekannte Eigenheiten bleiben erhalten (siehe Baseline-Spec `data-collection`):

* Zufallsbilder und Detektionsbeispiele werden auch ohne `-s` geschrieben.
* Das Label enthält nur die ERSTE Box, das Detektionsbild zeigt keine Boxen.
* Ordner werden nicht angelegt. Fehlt einer, wird eine Exception geworfen
  (wird im Change `systemd-service` zu einer Warnung).

Zeit und Zufall werden eingespeist (`name`, `rng`), damit Tests deterministisch sind.
"""

from __future__ import annotations

import glob
import os
import random
from typing import Sequence

import cv2

from hba.ports import Box

MAX_FILES = 1000
SAMPLE_VALUE = 42  # randrange(1, 100) == 42  ->  etwa 1 % der Frames
DETECTION_THRESHOLD = 90  # randrange(1, 100) > 90  ->  etwa 9 % der Frames mit Detektion


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
    def __init__(self, base_path: str, save_all: bool, rng: random.Random, max_files_per_folder: int = MAX_FILES):
        self.base_path = base_path
        self.save_all = save_all
        self.rng = rng
        self.max_files_per_folder = max_files_per_folder

    def _path(self, *parts: str) -> str:
        return os.path.join(self.base_path, *parts)

    def record_frame(self, name: str, crop) -> None:
        """Schritt vor der Erkennung: `-s` und die 1-%-Stichprobe (Ausschnitt 960x426)."""
        if self.save_all:
            _write_image(self._path("images", "crop", name + ".png"), crop)
        if self.rng.randrange(1, 100) == SAMPLE_VALUE:
            _write_image(self._path("images", "random", name + ".png"), crop)
            max_files(self._path("images", "random"), self.max_files_per_folder)

    def record_detection(self, name: str, model_input, boxes: Sequence[Box]) -> None:
        """Schritt nach der Erkennung: in etwa 9 % der Frames mit Boxen Bild und Label der ersten Box."""
        if len(boxes) == 0:
            return
        if self.rng.randrange(1, 100) > DETECTION_THRESHOLD:
            _write_image(self._path("images", "detections", name + ".png"), model_input)
            first = boxes[0]
            with open(self._path("labels", "detections", name + ".txt"), "w") as handle:
                handle.write(label_line(first.cls, first))
            max_files(self._path("images", "detections"), self.max_files_per_folder)
            max_files(self._path("labels", "detections"), self.max_files_per_folder)
