"""Referenzimplementierung der ALTEN Entscheidungslogik (nur erste Box zählt) für Vergleichstests.

Bewusst unabhängig von `src/hba/decision.py`, damit sie sich nicht mit dem Produktivcode ändert.
Entspricht `legacy/yolov8.py`, Zeilen 211 bis 234 und 288. Geometrie der ersten Box:
Breite < 500 und obere Kante > 160. Die Konfidenz wird hier nicht modelliert; die Auszüge
und Property-Tests verwenden Konfidenzen über der Schwelle.
"""

from __future__ import annotations

import gzip
import json
import os

DATA = os.path.join(os.path.dirname(__file__), "data")
LOGS = ("17183156523746762", "17199608122269757")
SKIP_START = 40  # Die ersten Frames: das Original setzte den Startzeitpunkt vor dem Laden des Modells


def load_frames(name):
    path = os.path.join(DATA, name + ".jsonl.gz")
    with gzip.open(path, "rt") as handle:
        return [json.loads(line) for line in handle]


def _relevant(box):
    x1, y1, x2, _ = box[0], box[1], box[2], box[3]
    return (x2 - x1) < 500 and y1 > 160


def legacy_statuses(frames, start_seconds):
    """Status je Frame nach der alten Logik. Frames: dicts mit `b` (Boxen), `td`, `ts`, `t0`."""
    last_detect, last_throttle = start_seconds, 0
    out = []
    for frame in frames:
        boxes = frame["b"]
        detect_seconds = int(frame.get("td") or frame["t0"])
        if boxes:
            if _relevant(boxes[0]) and last_throttle + 1 <= detect_seconds:
                last_detect = detect_seconds
            last_throttle = detect_seconds
        out.append(1 if last_detect + 3 <= int(frame["ts"]) else 0)
    return out
