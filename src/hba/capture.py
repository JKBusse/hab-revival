"""Bildaufbereitung (und später der Kamera-Adapter).

Verhalten wie im Legacy-Skript `legacy/yolov8.py`, Zeilen 179 bis 197.
"""

from __future__ import annotations

import logging
import os
import time

import cv2

# Legacy-Werte (werden in `config-file` konfigurierbar)
HOOD_ROWS = 850  # Motorhauben-Spiegelung entfernen: Zeilen 0..850
CROP_ROWS = (212, 638)
CROP_COLS = (400, 1360)
MODEL_SIZE = (640, 640)


def prepare_frame(frame):
    """Dreht den Frame um 180 Grad und liefert Ausschnitt und Modell-Eingabe.

    Rückgabe: (crop, model_input)
      crop         960x426, vor der Skalierung (wird für `-s` und Stichproben gespeichert)
      model_input  640x640, mit INTER_AREA skaliert (Seitenverhältnis nicht erhalten)
    """
    img = cv2.rotate(frame, cv2.ROTATE_180)
    img = img[0:HOOD_ROWS, 0:1920]
    crop = img[CROP_ROWS[0]:CROP_ROWS[1], CROP_COLS[0]:CROP_COLS[1]]
    model_input = cv2.resize(crop, MODEL_SIZE, interpolation=cv2.INTER_AREA)
    return crop, model_input


CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080


class OpenCvCamera:
    """Kamera-Adapter wie `initialize_camera` im Original (Zeilen 106 bis 136).

    Legacy-Eigenheit: Schlägt der erste `v4l2-ctl`-Befehl fehl, wird nur
    `initialize_camera: ERROR!` geloggt. Die übrigen Einstellungen (Belichtung,
    Auflösung) entfallen, das Programm läuft aber weiter.
    """

    def __init__(
        self,
        device: int = 0,
        exposure="1",
        exposure_time="700",
        brightness=None,
        logger: logging.Logger | None = None,
        run=os.system,
        sleep=time.sleep,
        capture_factory=cv2.VideoCapture,
    ):
        self.device = device
        self._capture = capture_factory(device)
        self._capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.initialized = self._configure(exposure, exposure_time, brightness, run, sleep)
        if logger is not None:
            if self.initialized:
                logger.info("initialize_camera: OK")
            else:
                logger.error("initialize_camera: ERROR!")

    def _configure(self, exposure, exposure_time, brightness, run, sleep) -> bool:
        exposure_mode = exposure
        if brightness:
            exposure_mode = 3
        base = "v4l2-ctl --device /dev/video" + str(self.device) + " --set-ctrl="
        if run(base + "power_line_frequency=1") != 0:  # 50 Hz
            return False
        run(base + "auto_exposure=" + str(exposure_mode))
        run(base + "exposure_time_absolute=" + str(exposure_time))
        run(base + "exposure_dynamic_framerate=0")
        if brightness:
            run(base + "brightness=" + str(brightness))
        sleep(1)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        print(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        return True

    def read(self):
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise RuntimeError("camera.read() lieferte kein Bild")
        return frame

    def release(self) -> None:
        self._capture.release()
