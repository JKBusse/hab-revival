"""Entscheidung: Fernlicht erlaubt (1) oder abgeblendet (0).

Reine Funktion mit explizitem Zustand, ohne Uhr und ohne Hardware. Sie bildet die
Logik aus `legacy/yolov8.py` (Zeilen 138, 211 bis 234, 288) einschließlich der
bekannten Eigenheiten nach, damit sich der Umbau gegen die Baseline prüfen lässt:

* Die Geometrie bewertet nur die ERSTE Box, die Konfidenz nur die LETZTE Box
  (Folge-Change `multi-box-decision`).
* Die Drosselung hängt nur davon ab, ob der Frame überhaupt Boxen enthielt.

Zeiten sind ganze Sekunden (`int(time.time())`). Das Original liest die Uhr an zwei
Stellen (bei der Detektion und beim Status), daher zwei Argumente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from hba.ports import Box
from hba.relevance import is_relevant

HOLD_SECONDS = 3  # so lange nach der letzten Detektion bleibt abgeblendet
THROTTLE_SECONDS = 1  # Aktualisierung höchstens einmal pro ganzer Sekunde


@dataclass(frozen=True)
class DecisionState:
    last_detect: int  # Legacy: lastDetectTimer
    last_frame_with_boxes: int  # Legacy: lastDetectTimer1 (Drossel)


def initial_state(start_seconds: int) -> DecisionState:
    """Beim Start gilt die Startzeit als letzte Detektion: die ersten 3 s bleiben abgeblendet."""
    return DecisionState(last_detect=start_seconds, last_frame_with_boxes=0)


def decide(
    state: DecisionState,
    boxes: Sequence[Box],
    detect_seconds: int,
    status_seconds: int,
    conf_threshold: float,
) -> tuple[DecisionState, int]:
    """Liefert den neuen Zustand und den Status (1 = Fernlicht erlaubt, 0 = abgeblendet)."""
    last_detect = state.last_detect
    last_frame = state.last_frame_with_boxes

    if len(boxes) > 0:
        # Legacy-Eigenheit: Geometrie der ersten, Konfidenz der letzten Box.
        if is_relevant(boxes[0]) and boxes[-1].conf >= conf_threshold:
            if last_frame + THROTTLE_SECONDS <= detect_seconds:
                last_detect = detect_seconds
        last_frame = detect_seconds

    status = 1 if last_detect + HOLD_SECONDS <= status_seconds else 0
    return DecisionState(last_detect, last_frame), status
