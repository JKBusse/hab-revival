import os
import random

import numpy as np
import pytest

from hba.ports import Box
from hba.recorder import MAX_FILES, Recorder, label_line, max_files, timestamp_name


class ScriptedRandom:
    """Liefert vorgegebene randrange-Werte und merkt sich die Aufrufe."""

    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randrange(self, start, stop):
        self.calls.append((start, stop))
        return self.values.pop(0)


@pytest.fixture
def base(tmp_path):
    for sub in ("images/crop", "images/random", "images/detections", "labels/detections", "log"):
        (tmp_path / sub).mkdir(parents=True)
    return tmp_path


CROP = np.zeros((426, 960, 3), dtype=np.uint8)
MODEL_INPUT = np.zeros((640, 640, 3), dtype=np.uint8)


def files(base, sub):
    return sorted(os.listdir(base / sub))


def test_timestamp_name_matches_example():
    assert timestamp_name(1698365548.2767072) == "16983655482767072"


def test_save_flag_writes_crop_each_frame(base):
    rec = Recorder(str(base) + "/", save_all=True, rng=ScriptedRandom([1, 1]))
    rec.record_frame("a", CROP)
    rec.record_frame("b", CROP)
    assert files(base, "images/crop") == ["a.png", "b.png"]


def test_without_save_flag_no_crops(base):
    rec = Recorder(str(base), save_all=False, rng=ScriptedRandom([1]))
    rec.record_frame("a", CROP)
    assert files(base, "images/crop") == []


def test_random_sample_only_for_value_42_even_without_save_flag(base):
    rng = ScriptedRandom([41, 42, 43])
    rec = Recorder(str(base), save_all=False, rng=rng)
    for name in ("a", "b", "c"):
        rec.record_frame(name, CROP)
    assert files(base, "images/random") == ["b.png"]
    assert rng.calls == [(1, 100)] * 3


def test_random_folder_limit_deletes_oldest_first(base):
    folder = base / "images/random"
    for i in range(5):
        path = folder / f"old{i}.png"
        path.write_bytes(b"x")
        os.utime(path, (1000 + i, 1000 + i))  # old0 ist am ältesten
    rec = Recorder(str(base), save_all=False, rng=ScriptedRandom([42]), max_files_per_folder=3)
    rec.record_frame("new", CROP)
    remaining = files(base, "images/random")
    assert len(remaining) == 3
    assert "new.png" in remaining
    assert "old0.png" not in remaining and "old1.png" not in remaining and "old2.png" not in remaining


def test_default_limit_is_1000():
    assert MAX_FILES == 1000
    assert Recorder("x", False, random.Random(0)).max_files_per_folder == 1000


def test_max_files_function_keeps_limit(tmp_path):
    for i in range(4):
        p = tmp_path / f"{i}.png"
        p.write_bytes(b"x")
        os.utime(p, (i, i))
    max_files(str(tmp_path), max_files=2)
    assert sorted(os.listdir(tmp_path)) == ["2.png", "3.png"]


FIRST = Box(x1=100.4, y1=200.2, x2=180.6, y2=300.8, cls=1, conf=0.9)
SECOND = Box(x1=300, y1=250, x2=380, y2=330, cls=0, conf=0.8)


def legacy_label(cls, cords_float):
    """make_label aus legacy/yolov8.py, Zeilen 158 bis 173, auf Werte reduziert."""
    leng = cords_float[2] - cords_float[0]
    hig = cords_float[3] - cords_float[1]
    cord = [round(x) for x in cords_float]
    xCenter = cord[0] + (leng / 2)
    xCenter = xCenter / 640
    yCenter = cord[1] + (hig / 2)
    yCenter = yCenter / 640
    xWidth = leng / 640
    yHeight = hig / 640
    return str(int(cls)) + " " + str(str(xCenter) + " " + str(yCenter) + " " + str(xWidth) + " " + str(yHeight))


def test_label_matches_legacy_formatting():
    expected = legacy_label(1, [100.4, 200.2, 180.6, 300.8])
    assert label_line(1, FIRST) == expected


def test_detection_example_writes_image_and_first_box_label_only(base):
    rec = Recorder(str(base), save_all=False, rng=ScriptedRandom([91]))
    rec.record_detection("t1", MODEL_INPUT, [FIRST, SECOND])
    assert files(base, "images/detections") == ["t1.png"]
    assert files(base, "labels/detections") == ["t1.txt"]
    text = (base / "labels/detections/t1.txt").read_text()
    assert text == legacy_label(1, [100.4, 200.2, 180.6, 300.8])
    assert "\n" not in text  # eine Zeile, ohne Zeilenende wie im Original


def test_detection_example_probability_boundary(base):
    rng = ScriptedRandom([90, 91])
    rec = Recorder(str(base), save_all=False, rng=rng)
    rec.record_detection("a", MODEL_INPUT, [FIRST])
    rec.record_detection("b", MODEL_INPUT, [FIRST])
    assert files(base, "images/detections") == ["b.png"]


def test_frame_without_boxes_does_not_draw_random_number(base):
    rng = ScriptedRandom([])
    rec = Recorder(str(base), save_all=False, rng=rng)
    rec.record_detection("a", MODEL_INPUT, [])
    assert rng.calls == []


def test_missing_folder_raises(tmp_path):
    rec = Recorder(str(tmp_path), save_all=True, rng=ScriptedRandom([1]))
    with pytest.raises(OSError):
        rec.record_frame("a", CROP)


def test_fixed_seed_gives_reproducible_selection(base):
    def run(seed):
        rec = Recorder(str(base), save_all=False, rng=random.Random(seed))
        picked = []
        for i in range(2000):
            before = set(os.listdir(base / "images/random"))
            rec.record_frame(f"f{i}", CROP)
            if set(os.listdir(base / "images/random")) != before:
                picked.append(i)
        for f in os.listdir(base / "images/random"):
            os.remove(base / "images/random" / f)
        return picked

    first = run(123)
    assert first == run(123)
    assert 5 <= len(first) <= 45  # etwa 1 % von 2000
