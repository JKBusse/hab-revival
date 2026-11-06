"""Relevanzfilter: Wann zählt eine Box als sinnvolle Detektion ("Active Area")?

Verhalten wie `get_active_area` in `legacy/yolov8.py`. Alle Werte beziehen sich auf das
640x640-Eingabebild. Die Schwellen kommen aus der Konfiguration (Standard 500 und 160).
"""

from __future__ import annotations

from hba.config import DEFAULTS, RelevanceConfig
from hba.ports import Box

MAX_WIDTH = DEFAULTS["relevance"]["max_width"]  # Breite muss kleiner sein
MIN_TOP = DEFAULTS["relevance"]["min_top"]  # obere Kante (y1) muss größer sein

_DEFAULT = RelevanceConfig(max_width=MAX_WIDTH, min_top=MIN_TOP)


def legacy_area_result(box: Box, relevance: RelevanceConfig | None = None):
    """Dreiwertiges Ergebnis wie im Original (für Log und Darstellung).

    True   Breite < 500 und obere Kante > 160
    None   Breite < 500, aber obere Kante <= 160 (das Original läuft ohne `return` aus)
    False  Breite >= 500

    Die Entscheidung unterscheidet nicht zwischen None und False, nur die Darstellung
    (None wird gelb gezeichnet) und der Logtext tun es.
    """
    cfg = relevance or _DEFAULT
    if box.width < cfg.max_width:
        if box.top > cfg.min_top:
            return True
        return None
    return False


def is_relevant(box: Box, relevance: RelevanceConfig | None = None) -> bool:
    return legacy_area_result(box, relevance) is True
