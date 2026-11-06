import logging
import subprocess
import sys

import cv2
import numpy as np
import pytest

from hba.capture import OpenCvCamera
from hba.detect import YoloDetector
from hba.ports import Box, Camera, Detector


# --- Kamera -----------------------------------------------------------------

class FakeCapture:
    def __init__(self, device):
        self.device = device
        self.sets = []
        self.frames = [(True, np.zeros((1080, 1920, 3), dtype=np.uint8))]

    def set(self, prop, value):
        self.sets.append((prop, value))

    def get(self, prop):
        return 1920.0

    def read(self):
        return self.frames.pop(0) if self.frames else (False, None)

    def release(self):
        self.released = True


def make_camera(run_results=None, **kwargs):
    commands = []
    results = list(run_results or [])

    def run(cmd):
        commands.append(cmd)
        return results.pop(0) if results else 0

    sleeps = []
    camera = OpenCvCamera(run=run, sleep=sleeps.append, capture_factory=FakeCapture, **kwargs)
    return camera, commands, sleeps


def test_default_setup_matches_legacy_commands():
    camera, commands, sleeps = make_camera()
    assert commands == [
        "v4l2-ctl --device /dev/video0 --set-ctrl=power_line_frequency=1",
        "v4l2-ctl --device /dev/video0 --set-ctrl=auto_exposure=1",
        "v4l2-ctl --device /dev/video0 --set-ctrl=exposure_time_absolute=700",
        "v4l2-ctl --device /dev/video0 --set-ctrl=exposure_dynamic_framerate=0",
    ]
    assert sleeps == [1]
    assert camera.initialized
    sets = camera._capture.sets
    assert (cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")) in sets
    assert (cv2.CAP_PROP_FRAME_WIDTH, 1920) in sets
    assert (cv2.CAP_PROP_FRAME_HEIGHT, 1080) in sets


def test_exposure_time_flag():
    _, commands, _ = make_camera(exposure_time="1200")
    assert "v4l2-ctl --device /dev/video0 --set-ctrl=exposure_time_absolute=1200" in commands


def test_brightness_switches_to_auto_exposure_mode_3():
    _, commands, _ = make_camera(brightness="50")
    assert "v4l2-ctl --device /dev/video0 --set-ctrl=auto_exposure=3" in commands
    assert commands[-1] == "v4l2-ctl --device /dev/video0 --set-ctrl=brightness=50"


def test_failed_first_command_logs_error_and_skips_rest(caplog):
    logger = logging.getLogger("HBA-test-camera")
    with caplog.at_level(logging.INFO, logger=logger.name):
        camera, commands, sleeps = make_camera(run_results=[1], logger=logger)
    assert not camera.initialized
    assert commands == ["v4l2-ctl --device /dev/video0 --set-ctrl=power_line_frequency=1"]
    assert sleeps == []
    assert not any(p == cv2.CAP_PROP_FRAME_WIDTH for p, _ in camera._capture.sets)
    assert "initialize_camera: ERROR!" in caplog.text


def test_ok_is_logged(caplog):
    logger = logging.getLogger("HBA-test-camera-ok")
    with caplog.at_level(logging.INFO, logger=logger.name):
        make_camera(logger=logger)
    assert "initialize_camera: OK" in caplog.text


def test_read_returns_frame_and_raises_when_none():
    camera, _, _ = make_camera()
    assert isinstance(camera, Camera)
    assert camera.read().shape == (1080, 1920, 3)
    with pytest.raises(RuntimeError):
        camera.read()


# --- Detektor ---------------------------------------------------------------

class FakeBoxes:
    def __init__(self, xyxy, conf, cls):
        self.xyxy = np.array(xyxy, dtype=float).reshape(-1, 4)
        self.conf = np.array(conf, dtype=float)
        self.cls = np.array(cls, dtype=float)

    def __len__(self):
        return len(self.conf)


class FakeResult:
    def __init__(self, boxes):
        self.boxes = boxes


def make_detector(boxes, **kwargs):
    calls = []

    def model(image, **kw):
        calls.append(kw)
        return iter([FakeResult(boxes)])

    kwargs.setdefault("cuda_available", lambda: True)
    detector = YoloDetector(model_path="x.pt", loader=lambda path: model, **kwargs)
    return detector, calls


def test_detector_returns_boxes_in_model_order():
    detector, _ = make_detector(FakeBoxes([[10, 20, 30, 40], [50, 60, 70, 80]], [0.9, 0.5], [1, 0]))
    assert isinstance(detector, Detector)
    boxes = detector.detect(np.zeros((640, 640, 3), dtype=np.uint8))
    assert boxes == [Box(10, 20, 30, 40, 1, 0.9), Box(50, 60, 70, 80, 0, 0.5)]


def test_detector_without_detections():
    detector, _ = make_detector(FakeBoxes([], [], []))
    assert detector.detect(np.zeros((640, 640, 3), dtype=np.uint8)) == []


def test_detector_passes_device_confidence_and_stream():
    detector, calls = make_detector(FakeBoxes([], [], []), device="0", conf=0.55)
    detector.detect(np.zeros((640, 640, 3), dtype=np.uint8))
    assert calls == [{"device": "0", "conf": 0.55, "stream": True}]


def test_detector_defaults_are_gpu_and_baseline_confidence():
    detector, _ = make_detector(FakeBoxes([], [], []))
    assert detector.device == "0" and detector.conf == 0.4


def test_importing_modules_does_not_load_torch_or_ultralytics():
    code = (
        "import sys, hba.detect, hba.ports, hba.decision, hba.relevance, hba.recorder;"
        "print(','.join(m for m in ('torch','ultralytics') if m in sys.modules))"
    )
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


# --- gpu-required: Standardgerät und CPU-Warnung ------------------------------------------

def test_default_device_is_the_first_gpu():
    from hba.detect import DEFAULT_DEVICE
    assert DEFAULT_DEVICE == "0"


def test_cpu_must_be_requested_explicitly_and_warns(caplog):
    logger = logging.getLogger("HBA-test-cpu")
    with caplog.at_level(logging.WARNING, logger=logger.name):
        detector, _ = make_detector(FakeBoxes([], [], []), device="cpu", logger=logger)
    assert detector.device == "cpu"
    assert any("nur für Entwicklung" in r.getMessage() for r in caplog.records)


def test_cpu_does_not_need_cuda(caplog):
    detector, _ = make_detector(FakeBoxes([], [], []), device="cpu", cuda_available=lambda: False)
    assert detector.device == "cpu"


@pytest.mark.parametrize("device", ["0", "cuda", "cuda:0"])
def test_gpu_device_without_cuda_raises(device):
    from hba.detect import GpuUnavailable
    with pytest.raises(GpuUnavailable):
        make_detector(FakeBoxes([], [], []), device=device, cuda_available=lambda: False)
