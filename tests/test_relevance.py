import pytest

from hba.ports import Box
from hba.relevance import is_relevant


def box(width, top):
    return Box(x1=100, y1=top, x2=100 + width, y2=top + 50, cls=1, conf=0.9)


@pytest.mark.parametrize(
    "width, top, expected, szenario",
    [
        (80, 250, True, "Normales Fahrzeug"),
        (520, 250, False, "Zu breite Box"),
        (80, 100, False, "Box zu weit oben im Bild"),
        # Grenzen: Breite muss KLEINER 500 sein, obere Kante GRÖSSER 160
        (499, 161, True, "knapp innerhalb"),
        (500, 250, False, "Breite genau 500"),
        (80, 160, False, "obere Kante genau 160"),
        (500, 160, False, "beide Grenzen genau"),
    ],
)
def test_active_area(width, top, expected, szenario):
    assert is_relevant(box(width, top)) is expected, szenario
