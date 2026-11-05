"""Kamera-Ersatz aus Bildern, für Läufe ohne Kamera (Entwicklung, Vergleichslauf).

Die Bilder der Datensätze sind bereits der 640x640-Eingang des Modells. `embed_in_frame`
legt ein solches Bild an die Stelle des Erkennungsausschnitts eines 1920x1080-Kameraframes
und dreht es um 180 Grad, sodass `prepare_frame` daraus wieder (nahezu) das Originalbild
macht. Es ist ein Ersatz für Pipeline-Läufe, kein Ersatz für einen Test der echten Kamera.
"""

from __future__ import annotations

import glob
import os
import re

import cv2
import numpy as np

from hba.capture import CROP_COLS, CROP_ROWS

FRAME_SHAPE = (1080, 1920, 3)
_TIMESTAMP_PNG = re.compile(r"^\d+\.png$")


def embed_in_frame(image640):
    crop_h = CROP_ROWS[1] - CROP_ROWS[0]
    crop_w = CROP_COLS[1] - CROP_COLS[0]
    crop = cv2.resize(image640, (crop_w, crop_h), interpolation=cv2.INTER_AREA)
    rotated = np.zeros(FRAME_SHAPE, dtype=np.uint8)
    rotated[CROP_ROWS[0]:CROP_ROWS[1], CROP_COLS[0]:CROP_COLS[1]] = crop
    return cv2.rotate(rotated, cv2.ROTATE_180)


class FolderCamera:
    """Liefert Kameraframes aus den Zeitstempel-PNG eines Ordners, in zeitlicher Reihenfolge.

    Mit `loop=True` beginnt die Folge nach dem letzten Bild von vorn. Sonst wirft `read()`
    wie eine ausgefallene Kamera.
    """

    def __init__(self, folder: str, loop: bool = True):
        names = sorted(
            (n for n in os.listdir(folder) if _TIMESTAMP_PNG.match(n)),
            key=lambda n: int(n[:-4]),
        )
        if not names:
            raise FileNotFoundError(f"Keine Zeitstempel-PNG in {folder}")
        self.paths = [os.path.join(folder, n) for n in names]
        self.loop = loop
        self._index = 0
        self.released = False

    def read(self):
        if self._index >= len(self.paths):
            if not self.loop:
                raise RuntimeError("FolderCamera: Bildfolge zu Ende")
            self._index = 0
        image = cv2.imread(self.paths[self._index])
        self._index += 1
        if image is None:
            raise RuntimeError(f"Bild nicht lesbar: {self.paths[self._index - 1]}")
        return embed_in_frame(image)

    def release(self) -> None:
        self.released = True
