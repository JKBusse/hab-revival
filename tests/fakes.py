"""Fakes für die Ports: erlauben Tests ohne Kamera, GPU, Mikrocontroller und Uhr."""

from __future__ import annotations

from typing import Sequence

from hba.ports import Box, Frame


class FakeCamera:
    """Spielt eine feste Bildfolge ab. Danach wirft `read()` wie eine ausgefallene Kamera."""

    def __init__(self, frames: Sequence[Frame]):
        self._frames = list(frames)
        self._index = 0
        self.released = False

    def read(self) -> Frame:
        if self._index >= len(self._frames):
            raise RuntimeError("FakeCamera: Bildfolge zu Ende")
        frame = self._frames[self._index]
        self._index += 1
        return frame

    def release(self) -> None:
        self.released = True


class FakeDetector:
    """Liefert je Aufruf die programmierten Boxen, in der Reihenfolge der Aufrufe."""

    def __init__(self, boxes_per_frame: Sequence[Sequence[Box]]):
        self._boxes = [list(b) for b in boxes_per_frame]
        self._index = 0
        self.images: list[Frame] = []

    def detect(self, image: Frame) -> Sequence[Box]:
        if self._index >= len(self._boxes):
            raise RuntimeError("FakeDetector: programmierte Folge zu Ende")
        self.images.append(image)
        boxes = self._boxes[self._index]
        self._index += 1
        return boxes


class FakeActuator:
    """Zeichnet jeden gesetzten Status auf."""

    def __init__(self) -> None:
        self.statuses: list[int] = []
        self.closed = False

    def set_status(self, status: int) -> None:
        self.statuses.append(status)

    def close(self) -> None:
        self.closed = True


class FakeClock:
    """Uhr, die nur auf Anweisung vorrückt."""

    def __init__(self, start: float = 1_700_000_000.0):
        self._now = start

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds

    def set(self, value: float) -> None:
        self._now = value
