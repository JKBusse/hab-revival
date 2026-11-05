"""Relevanzfilter: Wann zählt eine Box als sinnvolle Detektion ("Active Area")?

Verhalten wie `get_active_area` in `legacy/yolov8.py`. Alle Werte beziehen sich auf das
640x640-Eingabebild. Die Schwellen werden in `config-file` konfigurierbar.
"""

from __future__ import annotations

from hba.ports import Box

MAX_WIDTH = 500  # Breite muss kleiner sein
MIN_TOP = 160  # obere Kante (y1) muss größer sein


def legacy_area_result(box: Box):
    """Dreiwertiges Ergebnis wie im Original (für Log und Darstellung).

    True   Breite < 500 und obere Kante > 160
    None   Breite < 500, aber obere Kante <= 160 (das Original läuft ohne `return` aus)
    False  Breite >= 500

    Die Entscheidung unterscheidet nicht zwischen None und False, nur die Darstellung
    (None wird gelb gezeichnet) und der Logtext tun es.
    """
    if box.width < MAX_WIDTH:
        if box.top > MIN_TOP:
            return True
        return None
    return False


def is_relevant(box: Box) -> bool:
    return legacy_area_result(box) is True
