"""Detektor-Adapter für YOLOv8 (ultralytics).

`ultralytics` und `torch` werden erst beim Erzeugen des Adapters importiert, nicht auf
Modulebene. So lässt sich die gesamte Testsuite auf dem Mac ohne Torch ausführen.
Verhalten wie im Original (`legacy/yolov8.py`, Zeilen 140, 198 bis 214).
"""

from __future__ import annotations

from typing import Callable, Sequence

from hba.ports import Box

DEFAULT_MODEL = "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
DEFAULT_CONFIDENCE = 0.4
DEFAULT_DEVICE = "cpu"  # Legacy-Standard, wird in `gpu-required` geändert


def _load_yolo(model_path: str):
    from ultralytics import YOLO, settings

    settings.update({"sync": False})
    return YOLO(model_path)


class YoloDetector:
    def __init__(
        self,
        model_path: str = DEFAULT_MODEL,
        device: str = DEFAULT_DEVICE,
        conf: float = DEFAULT_CONFIDENCE,
        loader: Callable[[str], Callable] = _load_yolo,
    ):
        self.device = device
        self.conf = conf
        self._model = loader(model_path)

    def detect(self, image) -> Sequence[Box]:
        results = self._model(image, device=self.device, conf=self.conf, stream=True)
        boxes = None
        for result in results:  # wie im Original: das Ergebnis des letzten Durchlaufs zählt
            boxes = result.boxes
        if boxes is None:
            raise RuntimeError("Das Modell lieferte kein Ergebnis")
        conf = boxes.conf.tolist()
        cls = boxes.cls.tolist()
        out = []
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()
            out.append(Box(x1=x1, y1=y1, x2=x2, y2=y2, cls=int(cls[i]), conf=conf[i]))
        return out
