import cv2
import numpy as np
import pytest

from hba.capture import prepare_frame
from hba.ports import Camera
from hba.replay import FRAME_SHAPE, FolderCamera, embed_in_frame


def test_frame_has_camera_size():
    assert embed_in_frame(np.zeros((640, 640, 3), dtype=np.uint8)).shape == FRAME_SHAPE


def test_roundtrip_through_prepare_frame_is_close_to_original():
    rng = np.random.default_rng(1)
    # glattes Testbild: Verlauf, damit die zweifache Skalierung nur wenig verändert
    gradient = np.tile(np.linspace(0, 255, 640, dtype=np.uint8), (640, 1))
    original = np.dstack([gradient, gradient.T, gradient[::-1]])
    _, model_input = prepare_frame(embed_in_frame(original))
    assert model_input.shape == (640, 640, 3)
    assert np.abs(model_input.astype(int) - original.astype(int)).mean() < 3


def test_folder_camera_reads_in_time_order_and_loops(tmp_path):
    for name, value in (("200.png", 200), ("100.png", 100), ("note.png", 7)):
        cv2.imwrite(str(tmp_path / name), np.full((640, 640, 3), value, dtype=np.uint8))
    cam = FolderCamera(str(tmp_path), loop=True)
    assert isinstance(cam, Camera)
    values = [int(prepare_frame(cam.read())[1][320, 320, 0]) for _ in range(3)]
    assert values == [100, 200, 100]  # "note.png" ist kein Zeitstempel und wird ignoriert


def test_folder_camera_without_loop_raises_at_end(tmp_path):
    cv2.imwrite(str(tmp_path / "1.png"), np.zeros((640, 640, 3), dtype=np.uint8))
    cam = FolderCamera(str(tmp_path), loop=False)
    cam.read()
    with pytest.raises(RuntimeError):
        cam.read()


def test_folder_without_images_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        FolderCamera(str(tmp_path))
