"""Hauptschleife: setzt Kamera, Detektor, Entscheidung, Aktor, Recorder und Monitor zusammen.

Reihenfolge der Schritte pro Frame wie in `legacy/yolov8.py` (Zeilen 175 bis 319):
Frame lesen, aufbereiten, Aufnahmen vor der Erkennung, erkennen, bewerten und loggen,
Detektionsbeispiel, Darstellung (Stream, Fenster), Status entscheiden und senden,
Taste prüfen, Frame-Dauer loggen.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from hba import monitor
from hba.capture import prepare_frame
from hba.decision import decide, initial_state
from hba.ports import Actuator, Camera, Clock, Detector
from hba.recorder import Recorder, timestamp_name

KEY_STOP = ord("c")


@dataclass(frozen=True)
class Options:
    conf: float = 0.4
    video: bool = False
    stream: bool = False
    stream_dir: str = "/tmp"


@dataclass(frozen=True)
class StepResult:
    status: int
    stop: bool


class Pipeline:
    def __init__(
        self,
        camera: Camera,
        detector: Detector,
        actuator: Actuator,
        clock: Clock,
        recorder: Recorder,
        logger: logging.Logger,
        options: Options = Options(),
        start_seconds: int | None = None,
        show: Callable | None = None,
        poll_key: Callable[[], int] | None = None,
    ):
        self.camera = camera
        self.detector = detector
        self.actuator = actuator
        self.clock = clock
        self.recorder = recorder
        self.logger = logger
        self.options = options
        self.show = show
        self.poll_key = poll_key
        # Legacy: lastDetectTimer wird vor dem Laden des Modells gesetzt.
        self.state = initial_state(int(clock.now()) if start_seconds is None else start_seconds)
        self._old_time = 0.0  # Legacy: oldTime = 0, daher ist die erste Frame-Dauer riesig

    def warm_up(self) -> None:
        """Verarbeitet einen Frame ohne Entscheidung und ohne Aktor-Zugriff.

        Der erste Aufruf des Modells dauert deutlich länger (CUDA-Initialisierung) und würde
        sonst die Staleness-Regel des Aktors auslösen. Der Frame wird verworfen.
        """
        _, model_input = prepare_frame(self.camera.read())
        self.detector.detect(model_input)

    def step(self) -> StepResult:
        monitor.log_frame_start(self.logger)
        name = timestamp_name(self.clock.now())

        frame = self.camera.read()
        crop, model_input = prepare_frame(frame)
        self.recorder.record_frame(name, crop)

        boxes = self.detector.detect(model_input)
        monitor.log_boxes(self.logger, boxes)
        detect_seconds = int(self.clock.now())

        if len(boxes) > 0:
            self.recorder.record_detection(name, model_input, boxes)

        image = model_input
        if self.options.stream or self.options.video:
            image = monitor.annotate(model_input, boxes, logger=self.logger) if len(boxes) > 0 else model_input
        if self.options.video and self.show is not None:
            self.show(image)
        if self.options.stream:
            monitor.write_stream_frame(image, self.clock.now(), self.options.stream_dir)

        status_seconds = int(self.clock.now())
        self.state, status = decide(self.state, boxes, detect_seconds, status_seconds, self.options.conf)
        monitor.log_status(self.logger, status)
        self.actuator.set_status(status)

        stop = False
        if self.poll_key is not None and self.poll_key() == KEY_STOP:
            self.logger.info("Manual end C in CV2")
            stop = True

        now = self.clock.now()
        monitor.log_frame_duration(self.logger, now - self._old_time)
        self._old_time = now
        return StepResult(status=status, stop=stop)

    def run(self) -> None:
        """Läuft bis zur Taste `c`. Fehler (zum Beispiel ausgefallene Kamera) laufen nach außen."""
        while True:
            if self.step().stop:
                return
