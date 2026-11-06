"""Detektor-Adapter für YOLOv8 (ultralytics).

`ultralytics` und `torch` werden erst beim Erzeugen des Adapters importiert, nicht auf
Modulebene. So lässt sich die gesamte Testsuite auf dem Mac ohne Torch ausführen.
Verhalten wie im Original (`legacy/yolov8.py`, Zeilen 140, 198 bis 214).

Das Standardgerät ist die erste GPU. Die CPU gibt es nur auf ausdrückliche Anforderung
(`-d cpu`) und mit Warnung, ein CPU-Fallback existiert nicht (Change `gpu-required`).
"""

from __future__ import annotations

import logging
from typing import Callable, Sequence

from hba.ports import Box

DEFAULT_MODEL = "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
DEFAULT_CONFIDENCE = 0.4
DEFAULT_DEVICE = "0"  # erste GPU


class GpuUnavailable(RuntimeError):
    """Keine nutzbare GPU: CUDA fehlt oder der Warm-up scheitert."""


def is_gpu_device(device: str) -> bool:
    return str(device).strip().lower() != "cpu"


def is_cuda_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "cuda" in text or "cudnn" in text


def _cuda_available() -> bool:
    import torch

    return bool(torch.cuda.is_available())


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
        cuda_available: Callable[[], bool] = _cuda_available,
        logger: logging.Logger | None = None,
    ):
        self.device = device
        self.conf = conf
        log = logger if logger is not None else logging.getLogger("HBA")
        if is_gpu_device(device):
            if not cuda_available():
                raise GpuUnavailable("CUDA ist nicht verfügbar")
        else:
            log.warning("Gerät cpu: nur für Entwicklung und Tests gedacht, im Betrieb ist die GPU vorgesehen")
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
