"""Entscheidung: Fernlicht erlaubt (1) oder abgeblendet (0).

Reine Funktion mit explizitem Zustand, ohne Uhr und ohne Hardware. Ein Frame aktualisiert den
Zeitpunkt der letzten Detektion, sobald MINDESTENS EINE Box relevant ist (Geometrie der Aktiven
Fläche und Konfidenz ab dem Schwellwert), unabhängig von ihrer Position in der Liste.

Die Drosselung hängt nur davon ab, ob der Frame überhaupt Boxen enthielt, nicht von deren
Relevanz (unverändert gegenüber dem Original, `legacy/yolov8.py`, Zeilen 211 bis 234 und 288).

Zeiten sind ganze Sekunden (`int(time.time())`). Das Original liest die Uhr an zwei Stellen
(bei der Detektion und beim Status), daher zwei Argumente.

Nie weniger Abblenden als vorher (Change `multi-box-decision`): Die Menge der Frames, die
aktualisieren, ist eine Obermenge der früheren (erste Box relevant => irgendeine Box relevant).
Damit ist der Zeitpunkt der letzten Detektion nie früher und der Status nie höher als bei der
alten Logik. Das belegen der Replay mit echten Logs und der Property-Test.
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
        if any(is_relevant(box) and box.conf >= conf_threshold for box in boxes):
            if last_frame + THROTTLE_SECONDS <= detect_seconds:
                last_detect = detect_seconds
        last_frame = detect_seconds

    status = 1 if last_detect + HOLD_SECONDS <= status_seconds else 0
    return DecisionState(last_detect, last_frame), status
