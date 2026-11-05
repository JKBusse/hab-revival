"""Bildaufbereitung (und später der Kamera-Adapter).

Verhalten wie im Legacy-Skript `legacy/yolov8.py`, Zeilen 179 bis 197.
"""

from __future__ import annotations

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
