import pytest

from hba.ports import Actuator, Box, Camera, Clock, Detector
from fakes import FakeActuator, FakeCamera, FakeClock, FakeDetector


def car(y1=250):
    return Box(x1=100, y1=y1, x2=180, y2=y1 + 50, cls=1, conf=0.9)


def test_fakes_satisfy_the_ports():
    assert isinstance(FakeCamera([]), Camera)
    assert isinstance(FakeDetector([]), Detector)
    assert isinstance(FakeActuator(), Actuator)
    assert isinstance(FakeClock(), Clock)


def test_programmed_sequence_is_replayed_unchanged():
    frames = ["f0", "f1", "f2"]
    programmed = [[], [car()], [car(100), car(300)]]
    camera, detector, actuator, clock = FakeCamera(frames), FakeDetector(programmed), FakeActuator(), FakeClock()

    seen_frames, seen_boxes, seen_times = [], [], []
    for status in (0, 1, 0):
        frame = camera.read()
        boxes = detector.detect(frame)
        seen_frames.append(frame)
        seen_boxes.append(list(boxes))
        seen_times.append(clock.now())
        actuator.set_status(status)
        clock.advance(0.1)

    assert seen_frames == frames
    assert seen_boxes == programmed
    assert actuator.statuses == [0, 1, 0]
    assert seen_times == pytest.approx([1_700_000_000.0, 1_700_000_000.1, 1_700_000_000.2])
    assert detector.images == frames


def test_exhausted_camera_raises():
    camera = FakeCamera(["only"])
    camera.read()
    with pytest.raises(RuntimeError):
        camera.read()
