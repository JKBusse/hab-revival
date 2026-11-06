"""Kommandozeile und Zusammenbau.

Alle Werte kommen aus `hba.config`: Kommandozeilen-Flag vor Konfigurationsdatei vor eingebautem
Standard. Die Flags tragen deshalb selbst keine Vorgabe (`None` = nicht angegeben). Die Standardwerte
stehen an einer Stelle, in `hba.config.DEFAULTS`.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time

from hba import exit_codes
from hba.config import ConfigError, LoadedConfig, load_config, resolve_config_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m hba",
        description="High Beam Assist. Werte: Flag vor Konfigurationsdatei vor Standard.",
    )
    parser.add_argument("-v", "--video", help="Show Video Output", action="store_true", default=None)
    parser.add_argument("-S", "--stream", help="Stream Video Output", action="store_true", default=None)
    parser.add_argument("-s", "--save", help="Save the Caputerd Images", action="store_true", default=None)
    parser.add_argument("-c", "--conf", type=float, help="Minimal confidence for detecting Objects (Standard 0.4)")
    parser.add_argument("-d", "--device", help='Device for YOLO: GPU-Index oder "cpu" (Standard 0)')
    parser.add_argument("-m", "--model", help="Model for Prediction")
    parser.add_argument("-e", "--exposure", help="Auto Exposure Mode (1 = Manu, 3 = Auto, Standard 1)")
    parser.add_argument("-t", "--time", help="Exposure Time (0-5000, Standard 700)")
    parser.add_argument("-b", "--brightness", help="Brightness (-180-180)")
    parser.add_argument("-p", "--path", help="Path for Saving (Standard /mnt/hba-stick/HBA/)")
    parser.add_argument("--config", help="YAML-Konfigurationsdatei (sonst ./hba.yaml, falls vorhanden)")
    return parser


def load_runtime_config(args: argparse.Namespace) -> LoadedConfig:
    """Löst Datei und Flags auf. Wirft `ConfigError` bei ungültigen Werten."""
    path = resolve_config_path(args.config)
    flags = {key: value for key, value in vars(args).items() if key != "config"}
    return load_config(path, flags)


def main(argv=None) -> None:
    """Startet das System. Die Reihenfolge der Schritte entspricht dem Original."""
    args = build_parser().parse_args(argv)

    try:
        loaded = load_runtime_config(args)
    except ConfigError as exc:
        for error in exc.errors:
            print(f"Konfigurationsfehler: {error}", file=sys.stderr)
        sys.exit(exit_codes.EXIT_CONFIG)
    cfg = loaded.config

    # Schwere Importe erst nach dem Parsen und Prüfen, damit `--help` und Fehleingaben sofort enden.
    import cv2

    from hba import monitor
    from hba.actuator import ActuatorLink
    from hba.app import Options, Pipeline
    from hba.capture import OpenCvCamera
    from hba.detect import YoloDetector, is_gpu_device
    from hba.lifecycle import Lifecycle
    from hba.recorder import Recorder, timestamp_name
    from hba.startup import create_detector_or_exit, warm_up_or_exit
    from hba.watchdog import Watchdog

    start_name = timestamp_name(time.time())

    logger = monitor.setup_logger(os.path.join(cfg.recording.path, "log"), start_name)
    lifecycle = Lifecycle(logger)
    lifecycle.install()
    monitor.log_start(logger, start_name, str(args))
    monitor.log_config(logger, loaded)
    storage_ok = monitor.check_storage(cfg.recording.path, logger)
    print("Start...")
    print("Arguments: ", str(args))
    for warning in loaded.warnings:
        print(f"WARNUNG: {warning}", file=sys.stderr)

    actuator = ActuatorLink(port=cfg.serial.port, baudrate=cfg.serial.baudrate, logger=logger)
    lifecycle.actuator = actuator
    camera = OpenCvCamera.from_config(cfg.camera, logger=logger)
    start_seconds = int(time.time())  # Legacy: vor dem Laden des Modells
    detector = create_detector_or_exit(
        lambda: YoloDetector(
            model_path=cfg.detection.model, device=cfg.detection.device, conf=cfg.detection.conf, logger=logger
        ),
        lifecycle,
        logger,
    )
    logger.info("---initialisierung abgeschlossen--- \n")

    class SystemClock:
        def now(self) -> float:
            return time.time()

    watchdog = Watchdog(
        on_expire=lambda: lifecycle.hard_exit(
            exit_codes.EXIT_WATCHDOG, exit_codes.REASONS[exit_codes.EXIT_WATCHDOG]
        )
    )
    recorder = Recorder.from_config(cfg.recording, save_all=cfg.output.save, rng=random.Random(), logger=logger)
    if not storage_ok:
        recorder.disable_all()  # Ablage fehlt: Erkennung läuft weiter, Aufnahmen entfallen
    pipeline = Pipeline(
        camera=camera,
        detector=detector,
        actuator=actuator,
        clock=SystemClock(),
        recorder=recorder,
        logger=logger,
        options=Options.from_config(cfg),
        start_seconds=start_seconds,
        show=(lambda image: cv2.imshow("Result", image)) if cfg.output.video else None,
        poll_key=(lambda: cv2.waitKey(1)) if cfg.output.video else None,
        heartbeat=watchdog.beat,
    )
    # Erster Modellaufruf ist langsam: vor der Freigabe verwerfen. Auf der GPU gilt ein
    # Fehlschlag oder Hänger als "keine nutzbare GPU" (Exit-Code 3).
    warm_up_or_exit(pipeline, lifecycle, logger, gpu=is_gpu_device(cfg.detection.device))
    watchdog.start()
    pipeline.run()
    lifecycle.end()
