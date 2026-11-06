"""Bildaufbereitung (und später der Kamera-Adapter).

Verhalten wie im Legacy-Skript `legacy/yolov8.py`, Zeilen 179 bis 197.
"""

from __future__ import annotations

import logging
import os
import time

import cv2

from hba.config import DEFAULTS, MODEL_SIZE as _MODEL_SIZE, Config

# Standardwerte (= Legacy). Konfigurierbar über `hba.config`.
HOOD_ROWS = DEFAULTS["image"]["hood_rows"]  # Motorhauben-Spiegelung entfernen
CROP_ROWS = tuple(DEFAULTS["image"]["crop_rows"])
CROP_COLS = tuple(DEFAULTS["image"]["crop_cols"])
MODEL_SIZE = (_MODEL_SIZE, _MODEL_SIZE)

_DEFAULT_CONFIG = Config.defaults()


def prepare_frame(frame, config: Config | None = None):
    """Dreht den Frame (falls konfiguriert) um 180 Grad und liefert Ausschnitt und Modell-Eingabe.

    Rückgabe: (crop, model_input)
      crop         Ausschnitt vor der Skalierung (Standard 960x426, wird für `-s` und
                   Stichproben gespeichert)
      model_input  640x640, mit INTER_AREA skaliert (Seitenverhältnis nicht erhalten)
    """
    cfg = (config or _DEFAULT_CONFIG)
    img = cv2.rotate(frame, cv2.ROTATE_180) if cfg.camera.rotate_180 else frame
    img = img[0:cfg.image.hood_rows, 0:cfg.camera.width]
    r0, r1 = cfg.image.crop_rows
    c0, c1 = cfg.image.crop_cols
    crop = img[r0:r1, c0:c1]
    model_input = cv2.resize(crop, MODEL_SIZE, interpolation=cv2.INTER_AREA)
    return crop, model_input


CAMERA_WIDTH = DEFAULTS["camera"]["width"]
CAMERA_HEIGHT = DEFAULTS["camera"]["height"]


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
        width: int = CAMERA_WIDTH,
        height: int = CAMERA_HEIGHT,
        run=os.system,
        sleep=time.sleep,
        capture_factory=cv2.VideoCapture,
    ):
        self.device = device
        self.width = width
        self.height = height
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
        if brightness is not None:
            exposure_mode = 3
        base = "v4l2-ctl --device /dev/video" + str(self.device) + " --set-ctrl="
        if run(base + "power_line_frequency=1") != 0:  # 50 Hz
            return False
        run(base + "auto_exposure=" + str(exposure_mode))
        run(base + "exposure_time_absolute=" + str(exposure_time))
        run(base + "exposure_dynamic_framerate=0")
        if brightness is not None:
            run(base + "brightness=" + str(brightness))
        sleep(1)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        print(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        return True

    @classmethod
    def from_config(cls, camera, logger: logging.Logger | None = None, **kwargs):
        return cls(
            device=camera.device,
            exposure=camera.exposure,
            exposure_time=camera.exposure_time,
            brightness=camera.brightness,
            logger=logger,
            width=camera.width,
            height=camera.height,
            **kwargs,
        )

    def read(self):
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise RuntimeError("camera.read() lieferte kein Bild")
        return frame

    def release(self) -> None:
        self._capture.release()
