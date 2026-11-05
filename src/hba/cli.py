"""Kommandozeile und Zusammenbau. Flags und Standardwerte wie in der Baseline-Spec
`runtime-configuration` (zehn Flags)."""

from __future__ import annotations

import argparse
import os
import random
import time

DEFAULT_MODEL = "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
DEFAULT_PATH = "/mnt/hba-stick/HBA/"
DEFAULT_DEVICE = "cpu"  # Legacy-Standard, wird in `gpu-required` geändert


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m hba", description="High Beam Assist")
    parser.add_argument("-v", "--video", help="Show Video Output", action="store_true")
    parser.add_argument("-S", "--stream", help="Stream Video Output", action="store_true")
    parser.add_argument("-s", "--save", help="Save the Caputerd Images", action="store_true")
    parser.add_argument("-c", "--conf", type=float, default=0.4, help="Minimal confidence for detecting Objects")
    parser.add_argument("-d", "--device", default=DEFAULT_DEVICE, help="Device for YOLO")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Model for Prediction")
    parser.add_argument("-e", "--exposure", default="1", help="Auto Exposure Mode (1 = Manu, 3 = Auto)")
    parser.add_argument("-t", "--time", default="700", help="Exposure Time (0-5000)")
    parser.add_argument("-b", "--brightness", help="Brightness (-180-180)")
    parser.add_argument("-p", "--path", default=DEFAULT_PATH, help="Path for Saving")
    return parser


def main(argv=None) -> None:
    """Startet das System. Die Reihenfolge der Schritte entspricht dem Original."""
    args = build_parser().parse_args(argv)

    # Schwere Importe erst nach dem Parsen, damit `--help` und Fehleingaben sofort enden.
    import cv2

    from hba import monitor
    from hba.actuator import SerialActuator
    from hba.app import Options, Pipeline
    from hba.capture import OpenCvCamera
    from hba.detect import YoloDetector
    from hba.lifecycle import Lifecycle
    from hba.recorder import Recorder, timestamp_name

    start_name = timestamp_name(time.time())

    logger = monitor.setup_logger(os.path.join(args.path, "log"), start_name)
    lifecycle = Lifecycle(logger)
    lifecycle.install()
    monitor.log_start(logger, start_name, str(args))
    print("Start...")
    print("Arguments: ", str(args))

    actuator = SerialActuator(logger=logger)
    camera = OpenCvCamera(
        exposure=args.exposure, exposure_time=args.time, brightness=args.brightness, logger=logger
    )
    start_seconds = int(time.time())  # Legacy: vor dem Laden des Modells
    detector = YoloDetector(model_path=args.model, device=args.device, conf=args.conf)
    logger.info("---initialisierung abgeschlossen--- \n")

    class SystemClock:
        def now(self) -> float:
            return time.time()

    pipeline = Pipeline(
        camera=camera,
        detector=detector,
        actuator=actuator,
        clock=SystemClock(),
        recorder=Recorder(args.path, save_all=args.save, rng=random.Random()),
        logger=logger,
        options=Options(conf=args.conf, video=args.video, stream=args.stream),
        start_seconds=start_seconds,
        show=(lambda image: cv2.imshow("Result", image)) if args.video else None,
        poll_key=(lambda: cv2.waitKey(1)) if args.video else None,
    )
    pipeline.run()
    lifecycle.end()
