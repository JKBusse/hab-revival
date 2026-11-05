import logging
import os
import pty
import select

import numpy as np
import pytest

from fakes import FakeActuator, FakeCamera, FakeClock, FakeDetector
from hba import monitor
from hba.actuator import SerialActuator
from hba.app import Options, Pipeline
from hba.ports import Box
from hba.recorder import Recorder

T0 = 1_700_000_000.0
FRAME = np.zeros((1080, 1920, 3), dtype=np.uint8)
CAR = Box(x1=100, y1=250, x2=180, y2=300, cls=1, conf=0.9)


class NoRandom:
    """Zufall, der nie etwas speichert."""

    def randrange(self, a, b):
        return 1


@pytest.fixture
def logger(tmp_path):
    (tmp_path / "log").mkdir()
    lg = monitor.setup_logger(str(tmp_path / "log"), "run")
    yield lg
    for h in list(lg.handlers):
        lg.removeHandler(h)
        h.close()


def make_pipeline(tmp_path, logger, boxes, actuator, **kwargs):
    camera = FakeCamera([FRAME] * len(boxes))
    clock = FakeClock(T0)
    pipeline = Pipeline(
        camera, FakeDetector(boxes), actuator, clock,
        Recorder(str(tmp_path), save_all=False, rng=NoRandom()), logger, **kwargs,
    )
    return pipeline, clock


# Frame t=0..8: Fahrzeug nur in t=4 und t=5.
BOXES = [[], [], [], [], [CAR], [CAR], [], [], []]
EXPECTED = [0, 0, 0, 1, 0, 0, 0, 0, 1]


def test_programmed_sequence_gives_expected_status_sequence(tmp_path, logger):
    actuator = FakeActuator()
    pipeline, clock = make_pipeline(tmp_path, logger, BOXES, actuator)
    for _ in BOXES:
        pipeline.step()
        clock.advance(1.0)
    assert actuator.statuses == EXPECTED


def test_end_to_end_with_pseudo_terminal(tmp_path, logger):
    master, slave = pty.openpty()
    try:
        actuator = SerialActuator(port=os.ttyname(slave))
        pipeline, clock = make_pipeline(tmp_path, logger, BOXES, actuator)
        for _ in BOXES:
            pipeline.step()
            clock.advance(1.0)
        data = b""
        while select.select([master], [], [], 0.3)[0]:
            data += os.read(master, 1024)
        assert data == b"".join(b"%d\n" % s for s in EXPECTED)
        actuator.close()
    finally:
        os.close(master)
        os.close(slave)


def test_log_contains_legacy_message_types(tmp_path, logger):
    pipeline, clock = make_pipeline(tmp_path, logger, [[CAR], []], FakeActuator())
    for _ in range(2):
        pipeline.step()
        clock.advance(1.0)
    messages = [l.split(" - ", 3)[3] for l in (tmp_path / "log/run.log").read_text().splitlines()]
    assert messages.count("-Frame START-") == 2
    assert "Detections: 1" in messages and "Detections: 0" in messages
    assert "In active area 0 : True" in messages
    assert sum(m.startswith("HBA Status: ") for m in messages) == 2
    assert sum(m.startswith("DIFF: ") for m in messages) == 2


def test_first_frame_duration_is_huge_like_in_legacy(tmp_path, logger):
    pipeline, _ = make_pipeline(tmp_path, logger, [[]], FakeActuator())
    pipeline.step()
    diffs = [l for l in (tmp_path / "log/run.log").read_text().splitlines() if "DIFF:" in l]
    assert float(diffs[0].split("DIFF: ")[1]) == pytest.approx(T0)


def test_start_time_is_taken_from_argument_not_from_first_frame(tmp_path, logger):
    # Das Modell hat 2 s geladen: die Startsperre läuft schon seit T0, die erste Entscheidung bei T0+3.
    actuator = FakeActuator()
    pipeline, clock = make_pipeline(tmp_path, logger, [[]], actuator, start_seconds=int(T0))
    clock.advance(3.0)
    pipeline.step()
    assert actuator.statuses == [1]


def test_key_c_requests_stop(tmp_path, logger):
    pipeline, _ = make_pipeline(tmp_path, logger, [[]], FakeActuator(), poll_key=lambda: ord("c"))
    assert pipeline.step().stop
    assert "Manual end C in CV2" in (tmp_path / "log/run.log").read_text()


def test_run_stops_on_key_c(tmp_path, logger):
    keys = iter([-1, -1, ord("c")])
    pipeline, clock = make_pipeline(tmp_path, logger, [[]] * 5, FakeActuator(), poll_key=lambda: next(keys))
    pipeline.run()
    assert pipeline.camera._index == 3


def test_camera_failure_propagates(tmp_path, logger):
    pipeline, _ = make_pipeline(tmp_path, logger, [[]], FakeActuator())
    pipeline.step()
    with pytest.raises(RuntimeError):
        pipeline.step()


def test_stream_option_writes_annotated_frames(tmp_path, logger):
    stream_dir = tmp_path / "stream"
    stream_dir.mkdir()
    pipeline, _ = make_pipeline(
        tmp_path, logger, [[CAR]], FakeActuator(), options=Options(stream=True, stream_dir=str(stream_dir))
    )
    pipeline.step()
    written = os.listdir(stream_dir)
    assert len(written) == 1 and written[0].endswith(".png")


def test_detection_example_saved_before_boxes_are_drawn(tmp_path, logger):
    import cv2
    for sub in ("images/detections", "labels/detections"):
        (tmp_path / sub).mkdir(parents=True)

    class AlwaysSave:
        def randrange(self, a, b):
            return 99

    camera = FakeCamera([FRAME])
    pipeline = Pipeline(
        camera, FakeDetector([[CAR]]), FakeActuator(), FakeClock(T0),
        Recorder(str(tmp_path), save_all=False, rng=AlwaysSave()), logger,
        options=Options(stream=True, stream_dir=str(tmp_path)),
    )
    # randrange(...) == 42 nie, > 90 immer: 99 -> nur Detektionsbeispiel
    pipeline.step()
    saved = cv2.imread(str(tmp_path / "images/detections" / os.listdir(tmp_path / "images/detections")[0]))
    assert not saved.any()  # keine gezeichneten Boxen im gespeicherten Bild
