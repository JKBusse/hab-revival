"""Relevanzfilter: Wann zählt eine Box als sinnvolle Detektion ("Active Area")?

Verhalten wie `get_active_area` in `legacy/yolov8.py`. Alle Werte beziehen sich auf das
640x640-Eingabebild. Die Schwellen werden in `config-file` konfigurierbar.
"""

from __future__ import annotations

from hba.ports import Box

MAX_WIDTH = 500  # Breite muss kleiner sein
MIN_TOP = 160  # obere Kante (y1) muss größer sein


def is_relevant(box: Box) -> bool:
    return box.width < MAX_WIDTH and box.top > MIN_TOP
