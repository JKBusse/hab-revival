"""Geänderte Konfigurationswerte kommen in den Modulen an (Change config-file, Gruppe 2)."""

import os
import pty
import select
import time

import cv2
import numpy as np
import pytest

from hba import monitor
from hba.actuator import ActuatorLink
from hba.capture import OpenCvCamera, prepare_frame
from hba.config import Config, load_config
from hba.decision import DecisionState, decide, initial_state
from hba.ports import Box
from hba.recorder import Recorder
from hba.relevance import RelevanceConfig, is_relevant


def config_from(tmp_path, text):
    path = tmp_path / "c.yaml"
    path.write_text(text)
    return load_config(str(path), {}).config


FRAME = np.random.default_rng(3).integers(0, 256, size=(1080, 1920, 3), dtype=np.uint8)


# --- 2.1 Bildaufbereitung -----------------------------------------------------------------------

def test_default_config_gives_the_legacy_result_pixel_for_pixel():
    legacy = cv2.rotate(FRAME, cv2.ROTATE_180)[0:850, 0:1920][212:638, 400:1360]
    crop, model_input = prepare_frame(FRAME, Config.defaults())
    assert np.array_equal(crop, legacy)
    assert np.array_equal(model_input, cv2.resize(legacy, (640, 640), interpolation=cv2.INTER_AREA))
    assert np.array_equal(prepare_frame(FRAME)[0], crop)  # ohne Konfiguration dasselbe


def test_changed_crop_has_the_expected_size(tmp_path):
    cfg = config_from(tmp_path, "image:\n  crop_cols: [300, 1300]\n  crop_rows: [100, 600]\n")
    crop, model_input = prepare_frame(FRAME, cfg)
    assert crop.shape == (500, 1000, 3)
    assert model_input.shape == (640, 640, 3)


def test_hood_rows_cut_off_everything_below(tmp_path):
    cfg = config_from(tmp_path, "image:\n  hood_rows: 700\n  crop_rows: [212, 700]\n")
    assert prepare_frame(FRAME, cfg)[0].shape[0] == 700 - 212


def test_rotation_can_be_switched_off(tmp_path):
    cfg = config_from(tmp_path, "camera:\n  rotate_180: false\n")
    crop, _ = prepare_frame(FRAME, cfg)
    assert np.array_equal(crop, FRAME[0:850, 0:1920][212:638, 400:1360])


class FakeCapture:
    def __init__(self, device):
        self.device, self.sets = device, []

    def set(self, prop, value):
        self.sets.append((prop, value))

    def get(self, prop):
        return 0.0


def make_camera(cfg):
    commands = []
    cam = OpenCvCamera.from_config(
        cfg.camera, run=lambda c: commands.append(c) or 0, sleep=lambda s: None, capture_factory=FakeCapture
    )
    return cam, commands


def test_camera_uses_configured_resolution_device_and_exposure(tmp_path):
    cfg = config_from(
        tmp_path,
        "camera:\n  device: 2\n  width: 1280\n  height: 720\n  exposure_time: 1200\n"
        "image:\n  hood_rows: 700\n  crop_rows: [100, 600]\n  crop_cols: [200, 1000]\n",
    )
    cam, commands = make_camera(cfg)
    assert (cv2.CAP_PROP_FRAME_WIDTH, 1280) in cam._capture.sets
    assert (cv2.CAP_PROP_FRAME_HEIGHT, 720) in cam._capture.sets
    assert cam._capture.device == 2
    assert all("/dev/video2" in c for c in commands)
    assert "v4l2-ctl --device /dev/video2 --set-ctrl=exposure_time_absolute=1200" in commands


def test_default_camera_commands_are_unchanged():
    _, commands = make_camera(Config.defaults())
    assert commands == [
        "v4l2-ctl --device /dev/video0 --set-ctrl=power_line_frequency=1",
        "v4l2-ctl --device /dev/video0 --set-ctrl=auto_exposure=1",
        "v4l2-ctl --device /dev/video0 --set-ctrl=exposure_time_absolute=700",
        "v4l2-ctl --device /dev/video0 --set-ctrl=exposure_dynamic_framerate=0",
    ]


def test_brightness_zero_still_switches_to_auto_exposure(tmp_path):
    _, commands = make_camera(config_from(tmp_path, "camera:\n  brightness: 0\n"))
    assert "v4l2-ctl --device /dev/video0 --set-ctrl=auto_exposure=3" in commands
    assert commands[-1].endswith("brightness=0")


# --- 2.2 Relevanzfilter und Haltezeit -----------------------------------------------------------

def box(width, top):
    return Box(100, top, 100 + width, top + 50, cls=1, conf=0.9)


def test_changed_threshold_changes_relevance():
    loose = RelevanceConfig(max_width=500, min_top=100)
    assert is_relevant(box(80, 120), loose)
    assert not is_relevant(box(80, 120))  # Standard 160


def test_changed_max_width_changes_relevance():
    narrow = RelevanceConfig(max_width=60, min_top=160)
    assert not is_relevant(box(80, 250), narrow)
    assert is_relevant(box(50, 250), narrow)


def test_longer_hold_time_keeps_dimming_longer():
    state, _ = decide(initial_state(0), [box(80, 250)], 200, 200, 0.4, hold_seconds=5)
    assert decide(state, [], 204, 204, 0.4, hold_seconds=5)[1] == 0  # nach 4 s weiterhin abgeblendet
    assert decide(state, [], 205, 205, 0.4, hold_seconds=5)[1] == 1


def test_hold_time_also_governs_the_start():
    state = initial_state(100)
    assert decide(state, [], 103, 103, 0.4, hold_seconds=5)[1] == 0
    assert decide(state, [], 105, 105, 0.4, hold_seconds=5)[1] == 1
    assert decide(state, [], 103, 103, 0.4)[1] == 1  # Standard 3 s


def test_shorter_hold_time_releases_earlier():
    state, _ = decide(initial_state(0), [box(80, 250)], 200, 200, 0.4, hold_seconds=1)
    assert decide(state, [], 201, 201, 0.4, hold_seconds=1)[1] == 1


def test_color_follows_the_configured_area():
    black = np.zeros((640, 640, 3), dtype=np.uint8)
    b = Box(100, 120, 180, 170, cls=1, conf=0.9)  # y1=120: mit Standard zu weit oben
    default = monitor.annotate(black, [b])
    loose = monitor.annotate(black, [b], relevance=RelevanceConfig(500, 100))
    assert tuple(default[145, 87]) == (0, 255, 255)  # gelb
    assert tuple(loose[145, 87]) == (255, 255, 255)  # weiß: jetzt relevant


# --- 2.3 Serial, Wahrscheinlichkeiten, Dateilimit ----------------------------------------------------

def test_configured_serial_port_is_used(tmp_path):
    master, slave = pty.openpty()
    try:
        cfg = config_from(tmp_path, f"serial:\n  port: {os.ttyname(slave)}\n  baudrate: 19200\n")
        link = ActuatorLink(port=cfg.serial.port, baudrate=cfg.serial.baudrate)
        try:
            assert link.connected and link.baudrate == 19200
            link.set_status(0)
            data, end = b"", time.time() + 1.0
            while time.time() < end and not data:
                if select.select([master], [], [], 0.05)[0]:
                    data += os.read(master, 100)
            assert data.startswith(b"0")
        finally:
            link.close()
    finally:
        os.close(master)
        os.close(slave)


class FixedRandom:
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


@pytest.fixture
def folders(tmp_path):
    for sub in ("images/crop", "images/random", "images/detections", "labels/detections", "log"):
        (tmp_path / sub).mkdir(parents=True)
    return tmp_path


CROP = np.zeros((426, 960, 3), dtype=np.uint8)


def test_probability_zero_never_records_and_one_always_records(folders, tmp_path):
    never = config_from(tmp_path, f"recording:\n  path: {folders}\n  sample_probability: 0\n  detection_probability: 0\n")
    always = config_from(tmp_path, f"recording:\n  path: {folders}\n  sample_probability: 1\n  detection_probability: 1\n")
    Recorder.from_config(never.recording, False, FixedRandom(0.0)).record_frame("a", CROP)
    assert os.listdir(folders / "images/random") == []
    Recorder.from_config(always.recording, False, FixedRandom(0.999)).record_frame("b", CROP)
    assert os.listdir(folders / "images/random") == ["b.png"]


def test_configured_file_limit_is_applied(folders, tmp_path):
    cfg = config_from(tmp_path, f"recording:\n  path: {folders}\n  sample_probability: 1\n  max_files: 2\n")
    rec = Recorder.from_config(cfg.recording, False, FixedRandom(0.0))
    for i in range(5):
        rec.record_frame(f"f{i}", CROP)
        time.sleep(0.01)
    assert len(os.listdir(folders / "images/random")) == 2


def test_default_probabilities_equal_the_legacy_ones():
    rec = Config.defaults().recording
    assert rec.sample_probability == pytest.approx(1 / 99)
    assert rec.detection_probability == pytest.approx(9 / 99)
    assert rec.max_files == 1000
