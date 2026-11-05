"""Schnittstellen (Ports) zwischen Pipeline und Hardware.

Nur was Hardware oder Zeit berührt, liegt hinter einer Schnittstelle. Das Modul
importiert bewusst weder OpenCV noch Torch noch pyserial, damit es überall und
ohne Hardware importierbar ist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence, runtime_checkable

# Ein Bild ist ein numpy-Array (H x W x 3, BGR). Hier nur als Alias, damit dieses
# Modul numpy nicht importieren muss.
Frame = Any


@dataclass(frozen=True)
class Box:
    """Eine erkannte Box im Koordinatenraum des Eingabebilds (xyxy)."""

    x1: float
    y1: float
    x2: float
    y2: float
    cls: int  # 0 = back (Rücklichter), 1 = front (Scheinwerfer)
    conf: float

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def top(self) -> float:
        """Obere Kante (y1). Im Legacy-Code `hei`."""
        return self.y1


@runtime_checkable
class Camera(Protocol):
    def read(self) -> Frame:
        """Liefert den nächsten Frame. Wirft eine Exception, wenn keiner kommt."""
        ...

    def release(self) -> None: ...


@runtime_checkable
class Detector(Protocol):
    def detect(self, image: Frame) -> Sequence[Box]:
        """Boxen für ein 640x640-Eingabebild, in der Reihenfolge des Modells."""
        ...


@runtime_checkable
class Actuator(Protocol):
    def set_status(self, status: int) -> None:
        """Setzt den gewünschten Status (1 = Fernlicht erlaubt, 0 = abgeblendet).

        Darf nicht blockieren (siehe Change fail-safe-shutdown).
        """
        ...

    def close(self) -> None: ...


@runtime_checkable
class Clock(Protocol):
    def now(self) -> float:
        """Sekunden seit der Epoche, wie `time.time()`."""
        ...
