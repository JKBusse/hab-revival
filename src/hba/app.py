"""Hauptschleife: setzt Kamera, Detektor, Entscheidung, Aktor, Recorder und Monitor zusammen.

Reihenfolge der Schritte pro Frame wie in `legacy/yolov8.py` (Zeilen 175 bis 319):
Frame lesen, aufbereiten, Aufnahmen vor der Erkennung, erkennen, bewerten und loggen,
Detektionsbeispiel, Darstellung (Stream, Fenster), Status entscheiden und senden,
Taste prüfen, Frame-Dauer loggen.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Callable

from hba import monitor
from hba.capture import prepare_frame
from hba.config import Config
from hba.decision import decide, initial_state
from hba.detect import GpuUnavailable, is_cuda_error
from hba.ports import Actuator, Camera, Clock, Detector
from hba.recorder import Recorder, timestamp_name

KEY_STOP = ord("c")
WARMUP_SECONDS = 30.0


class WarmUpTimeout(GpuUnavailable):
    """Der Warm-up-Frame wurde nicht rechtzeitig fertig (hängende GPU)."""


@dataclass(frozen=True)
class Options:
    conf: float = 0.4
    video: bool = False
    stream: bool = False
    stream_dir: str = "/tmp"
    config: Config = Config.defaults()  # Bildaufbereitung, Aktive Fläche, Haltezeit

    @classmethod
    def from_config(cls, config: Config, stream_dir: str = "/tmp") -> "Options":
        return cls(
            conf=config.detection.conf,
            video=config.output.video,
            stream=config.output.stream,
            stream_dir=stream_dir,
            config=config,
        )


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
        heartbeat: Callable[[], None] | None = None,
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
        self.heartbeat = heartbeat  # meldet der Watchdog jeden fertigen Frame
        # Legacy: lastDetectTimer wird vor dem Laden des Modells gesetzt.
        self.state = initial_state(int(clock.now()) if start_seconds is None else start_seconds)
        self._old_time = 0.0  # Legacy: oldTime = 0, daher ist die erste Frame-Dauer riesig

    def warm_up(self, timeout: float | None = None) -> None:
        """Verarbeitet einen Frame ohne Entscheidung und ohne Aktor-Zugriff.

        Der erste Aufruf des Modells dauert deutlich länger (CUDA-Initialisierung) und würde
        sonst die Staleness-Regel des Aktors auslösen. Der Frame wird verworfen.

        Mit `timeout` läuft der Frame in einem eigenen Thread. Wird er nicht rechtzeitig
        fertig, wird `WarmUpTimeout` geworfen (der Thread bleibt dann hängen).
        """
        if timeout is None:
            self._warm_up_once()
            return
        outcome: dict = {}

        def work():
            try:
                self._warm_up_once()
            except BaseException as exc:  # an den Aufrufer weiterreichen
                outcome["error"] = exc

        thread = threading.Thread(target=work, name="warm-up", daemon=True)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            raise WarmUpTimeout(f"Warm-up-Frame nach {timeout:g} s nicht fertig")
        if "error" in outcome:
            raise outcome["error"]

    def _warm_up_once(self) -> None:
        _, model_input = prepare_frame(self.camera.read(), self.options.config)
        self.detector.detect(model_input)

    def step(self) -> StepResult:
        monitor.log_frame_start(self.logger)
        name = timestamp_name(self.clock.now())

        frame = self.camera.read()
        crop, model_input = prepare_frame(frame, self.options.config)
        self.recorder.record_frame(name, crop)

        boxes = self.detector.detect(model_input)
        monitor.log_boxes(self.logger, boxes, self.options.config.relevance)
        detect_seconds = int(self.clock.now())

        if len(boxes) > 0:
            self.recorder.record_detection(name, model_input, boxes)

        image = model_input
        if self.options.stream or self.options.video:
            image = monitor.annotate(model_input, boxes, logger=self.logger, relevance=self.options.config.relevance) if len(boxes) > 0 else model_input
        if self.options.video and self.show is not None:
            self.show(image)
        if self.options.stream:
            monitor.write_stream_frame(image, self.clock.now(), self.options.stream_dir)

        status_seconds = int(self.clock.now())
        self.state, status = decide(
            self.state, boxes, detect_seconds, status_seconds, self.options.conf,
            hold_seconds=self.options.config.decision.hold_seconds,
            relevance=self.options.config.relevance,
        )
        monitor.log_status(self.logger, status)
        self.actuator.set_status(status)

        stop = False
        if self.poll_key is not None and self.poll_key() == KEY_STOP:
            self.logger.info("Manual end C in CV2")
            stop = True

        now = self.clock.now()
        monitor.log_frame_duration(self.logger, now - self._old_time)
        self._old_time = now
        if self.heartbeat is not None:
            self.heartbeat()
        return StepResult(status=status, stop=stop)

    def run(self) -> None:
        """Läuft bis zur Taste `c`. Fehler (zum Beispiel ausgefallene Kamera) laufen nach außen."""
        while True:
            try:
                result = self.step()
            except Exception as exc:
                self.actuator.set_status(0)  # sofort abblenden, bevor das Programm endet
                if is_cuda_error(exc):
                    self.logger.error("CUDA-Fehler in der Inferenz: %s", exc)
                raise
            if result.stop:
                return
