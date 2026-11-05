import cv2
import numpy as np

from hba.capture import prepare_frame


def legacy_prepare(img):
    """Die Original-Zeilen aus legacy/yolov8.py (179, 184, 185, 197), unverändert."""
    img = cv2.rotate(img, cv2.ROTATE_180)
    img = img[0:850, 0:1920]  # Motorhaube Spiegelung Entfernung
    img = img[212:638, 400:1360]  # Ausschnitt
    crop = img.copy()
    img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_AREA)
    return crop, img


def make_test_image():
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(1080, 1920, 3), dtype=np.uint8)


def test_matches_legacy_pixel_for_pixel():
    frame = make_test_image()
    crop, model_input = prepare_frame(frame.copy())
    legacy_crop, legacy_input = legacy_prepare(frame.copy())
    assert np.array_equal(crop, legacy_crop)
    assert np.array_equal(model_input, legacy_input)


def test_shapes():
    crop, model_input = prepare_frame(make_test_image())
    assert crop.shape == (426, 960, 3)
    assert model_input.shape == (640, 640, 3)


def test_input_frame_is_not_modified():
    frame = make_test_image()
    before = frame.copy()
    prepare_frame(frame)
    assert np.array_equal(frame, before)


def test_rotation_is_180_degrees():
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame[1079, 1919] = (1, 2, 3)  # unten rechts
    crop, _ = prepare_frame(frame)
    # nach der Drehung liegt der Punkt bei (0, 0): Zeile 0 liegt ausserhalb des Ausschnitts (ab 212)
    assert not crop.any()
    frame2 = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame2[1080 - 1 - 212, 1920 - 1 - 400] = (9, 9, 9)  # landet nach Drehung bei (212, 400) = crop[0, 0]
    crop2, _ = prepare_frame(frame2)
    assert tuple(crop2[0, 0]) == (9, 9, 9)
