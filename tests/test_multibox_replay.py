"""Replay mit echten Fahrt-Logs und Property-Test (Change multi-box-decision).

Drei Ebenen:
1. Nachbau der alten Logik == geloggter Status (Vertrauen in die Baseline, exakt, ohne Toleranz)
2. neue Logik <= alte Logik (keine Regression): echte Logs und Zufallsfolgen
3. Konstruierte Frames für den Fehlerfall: siehe test_decision.py
"""

import random

import pytest

from hba.decision import decide, initial_state
from hba.ports import Box
from legacy_reference import LOGS, SKIP_START, legacy_statuses, load_frames

CONF = 0.4
ASSUMED_CONFIDENCE = 0.9  # Die Logs enthalten keine Konfidenz; das Modell filtert bereits mit der Schwelle.


def new_statuses(frames, start_seconds):
    state = initial_state(start_seconds)
    out = []
    for frame in frames:
        boxes = [Box(b[0], b[1], b[2], b[3], cls=1, conf=ASSUMED_CONFIDENCE) for b in frame["b"]]
        detect_seconds = int(frame.get("td") or frame["t0"])
        state, status = decide(state, boxes, detect_seconds, int(frame["ts"]), CONF)
        out.append(status)
    return out


# --- Ebene 1: die alte Logik reproduziert den geloggten Status ----------------------------

@pytest.mark.parametrize("name", LOGS)
def test_legacy_reference_reproduces_logged_status(name):
    frames = load_frames(name)
    reference = legacy_statuses(frames, int(frames[0]["t0"]))
    logged = [f["s"] for f in frames]
    deviations = [i for i in range(SKIP_START, len(frames)) if reference[i] != logged[i]]
    assert deviations == []


def test_extracts_have_the_expected_size():
    sizes = {name: len(load_frames(name)) for name in LOGS}
    assert sizes == {"17183156523746762": 22900, "17199608122269757": 21936}


# --- Ebene 2: neue Logik blendet nie weniger ab als die alte -------------------------------

@pytest.mark.parametrize("name", LOGS)
def test_new_logic_never_dims_less_on_real_logs(name):
    frames = load_frames(name)
    start = int(frames[0]["t0"])
    old, new = legacy_statuses(frames, start), new_statuses(frames, start)
    brighter = [i for i in range(len(frames)) if new[i] > old[i]]
    assert brighter == []


def random_frames(rng, count=80):
    t, frames = 1000, []
    for _ in range(count):
        t += rng.choice([0, 0, 0, 1, 1, 2, 4])  # auch Sprünge und mehrere Frames pro Sekunde
        boxes = []
        for _ in range(rng.choice([0, 0, 1, 1, 2, 3])):
            x1, y1 = rng.randrange(0, 300), rng.choice([50, 160, 161, 300])
            boxes.append([x1, y1, x1 + rng.choice([80, 499, 500, 600]), y1 + 50])
        frames.append({"b": boxes, "t0": t, "td": t, "ts": t + rng.choice([0, 0, 1])})
    return frames


@pytest.mark.parametrize("seed", range(300))
def test_property_new_logic_never_dims_less_on_random_sequences(seed):
    frames = random_frames(random.Random(seed))
    old, new = legacy_statuses(frames, 1000), new_statuses(frames, 1000)
    assert all(n <= o for n, o in zip(new, old))
