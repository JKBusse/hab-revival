import logging
import re

import cv2
import numpy as np
import pytest

from hba import monitor
from hba.ports import Box


@pytest.fixture
def logger(tmp_path):
    lg = monitor.setup_logger(str(tmp_path), "123")
    yield lg
    for h in list(lg.handlers):
        lg.removeHandler(h)
        h.close()


def read_log(tmp_path):
    return (tmp_path / "123.log").read_text().splitlines()


def test_log_line_format_and_frame_messages(tmp_path, logger):
    boxes = [
        Box(100, 250, 180, 300, cls=1, conf=0.9),  # True
        Box(100, 250, 700, 300, cls=1, conf=0.9),  # False (zu breit)
        Box(100, 100, 180, 150, cls=0, conf=0.9),  # None (zu hoch)
    ]
    monitor.log_frame_start(logger)
    monitor.log_boxes(logger, boxes)
    monitor.log_status(logger, 0)
    monitor.log_frame_duration(logger, 0.123456)
    lines = read_log(tmp_path)
    pattern = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3} - HBA - (INFO|CRITICAL|DEBUG) - ")
    assert all(pattern.match(line) for line in lines)
    messages = [line.split(" - ", 3)[3] for line in lines]
    assert messages[0] == "-Frame START-"
    assert "Detections: 3" in messages
    assert "In active area 0 : True" in messages
    assert "In active area 1 : False" in messages
    assert "In active area 2 : None" in messages
    assert any(m.startswith("Len: 80") and "Hei: 250" in m for m in messages)
    assert "HBA Status: 0" in messages
    assert messages[-1] == "DIFF: 0.1235"


def test_log_for_empty_frame(tmp_path, logger):
    monitor.log_frame_start(logger)
    monitor.log_boxes(logger, [])
    messages = [line.split(" - ", 3)[3] for line in read_log(tmp_path)]
    assert messages == ["-Frame START-", "Detections: 0"]


def test_start_and_end_messages(tmp_path, logger):
    monitor.log_start(logger, "123", "Namespace(video=False)")
    monitor.log_end(logger)
    text = (tmp_path / "123.log").read_text()
    assert "CRITICAL - ---START---" in text
    assert "Start Time: 123" in text
    assert "Arguments: Namespace(video=False)" in text
    assert "---END---" in text


def test_setup_twice_does_not_duplicate_lines(tmp_path):
    monitor.setup_logger(str(tmp_path), "123")
    lg = monitor.setup_logger(str(tmp_path), "123")
    monitor.log_frame_start(lg)
    assert len(read_log(tmp_path)) == 1
    for h in list(lg.handlers):
        lg.removeHandler(h)
        h.close()


def test_missing_log_folder_raises(tmp_path):
    with pytest.raises(OSError):
        monitor.setup_logger(str(tmp_path / "gibt-es-nicht"), "1")


BLACK = np.zeros((640, 640, 3), dtype=np.uint8)


def pixel_left_edge(image, box):
    """Pixel in der Mitte der linken Kante der gezeichneten Box (13 Pixel Abstand)."""
    return tuple(int(v) for v in image[(round(box.y1) + round(box.y2)) // 2, round(box.x1) - 13])


def test_colors_relevant_front_is_white():
    box = Box(100, 250, 180, 300, cls=1, conf=0.9)
    assert pixel_left_edge(monitor.annotate(BLACK, [box]), box) == (255, 255, 255)


def test_colors_relevant_back_is_red():
    box = Box(100, 250, 180, 300, cls=0, conf=0.9)
    assert pixel_left_edge(monitor.annotate(BLACK, [box]), box) == (0, 0, 255)


def test_colors_box_too_high_is_yellow():
    box = Box(100, 100, 180, 150, cls=1, conf=0.9)
    assert pixel_left_edge(monitor.annotate(BLACK, [box]), box) == (0, 255, 255)


def test_colors_too_wide_box_is_not_yellow_legacy_quirk():
    wide_front = Box(20, 250, 580, 300, cls=1, conf=0.9)
    wide_back = Box(20, 250, 580, 300, cls=0, conf=0.9)
    assert pixel_left_edge(monitor.annotate(BLACK, [wide_front]), wide_front) == (255, 255, 255)
    assert pixel_left_edge(monitor.annotate(BLACK, [wide_back]), wide_back) == (0, 0, 255)


def test_margin_is_13_pixels_and_original_unchanged():
    box = Box(100, 250, 180, 300, cls=1, conf=0.9)
    original = BLACK.copy()
    out = monitor.annotate(BLACK, [box])
    assert np.array_equal(BLACK, original)  # Eingangsbild bleibt unverändert
    y = (250 + 300) // 2
    assert tuple(out[y, 100]) == (0, 0, 0)  # an der Box selbst nichts
    assert tuple(out[y, 87]) == (255, 255, 255)  # 13 Pixel daneben


def test_annotate_with_logger_logs_rounded_area(tmp_path, logger):
    box = Box(100.4, 250.2, 180.6, 300.8, cls=1, conf=0.9)
    monitor.annotate(BLACK, [box], logger=logger)
    messages = [line.split(" - ", 3)[3] for line in read_log(tmp_path)]
    assert messages[0] == "cord0: 100 cord1: 250 cord2: 181 cord3: 301"


def test_stream_frame_written_with_timestamp_name(tmp_path):
    path = monitor.write_stream_frame(BLACK, 1698365548.2767072, str(tmp_path))
    assert path == str(tmp_path / "16983655482767072.png")
    assert cv2.imread(path).shape == (640, 640, 3)
