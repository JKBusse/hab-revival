"""Vergleichslauf ohne Kamera: Bildordner statt Kamera, echter Detektor, Serial über ein Pseudo-Terminal.

Beispiel (auf hba1):
    .venv/bin/python tools/replay_run.py --images ~/HBA4v2Dataset/train/images -d 0 --seconds 300

Wertet am Ende das Log und die Bytes am Aktor aus (Meldungstypen, Frame-Dauer, Statusfolge).
Prüft NICHT die echte Kamera (/dev/video0, v4l2-ctl).
"""

from __future__ import annotations

import argparse
import os
import pty
import random
import re
import select
import statistics
import threading
import time

from hba import monitor
from hba.actuator import SerialActuator
from hba.app import Options, Pipeline
from hba.detect import YoloDetector
from hba.recorder import Recorder, timestamp_name
from hba.replay import FolderCamera

LEGACY_MESSAGE_TYPES = [
    "-Frame START-", "Detections:", "cord0:", "Len:", "In active area", "HBA Status:", "DIFF:",
]


class SystemClock:
    def now(self) -> float:
        return time.time()


def drain(master, sink: bytearray, stop: threading.Event) -> None:
    while not stop.is_set():
        if select.select([master], [], [], 0.2)[0]:
            sink.extend(os.read(master, 4096))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--images", required=True)
    p.add_argument("-d", "--device", default="cpu")
    p.add_argument("-m", "--model", default="/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt")
    p.add_argument("-c", "--conf", type=float, default=0.4)
    p.add_argument("--seconds", type=float, default=60)
    p.add_argument("--out", default=os.path.expanduser("~/hba-replay"))
    args = p.parse_args()

    for sub in ("log", "images/crop", "images/random", "images/detections", "labels/detections"):
        os.makedirs(os.path.join(args.out, sub), exist_ok=True)  # Recorder legt keine Ordner an (Legacy)
    start_name = timestamp_name(time.time())
    logger = monitor.setup_logger(os.path.join(args.out, "log"), start_name)
    monitor.log_start(logger, start_name, str(args))

    master, slave = pty.openpty()
    received, stop = bytearray(), threading.Event()
    threading.Thread(target=drain, args=(master, received, stop), daemon=True).start()

    actuator = SerialActuator(port=os.ttyname(slave), logger=logger)
    camera = FolderCamera(args.images, loop=True)
    clock = SystemClock()
    start_seconds = int(clock.now())
    detector = YoloDetector(model_path=args.model, device=args.device, conf=args.conf)
    logger.info("---initialisierung abgeschlossen--- \n")
    pipeline = Pipeline(
        camera, detector, actuator, clock,
        Recorder(args.out, save_all=False, rng=random.Random(0)),
        logger, Options(conf=args.conf), start_seconds=start_seconds,
    )

    end = time.time() + args.seconds
    frames = 0
    while time.time() < end:
        pipeline.step()
        frames += 1
    monitor.log_end(logger)
    time.sleep(0.5)
    stop.set()

    log_path = os.path.join(args.out, "log", start_name + ".log")
    lines = open(log_path).read().splitlines()
    messages = [l.split(" - ", 3)[3] for l in lines if l.count(" - ") >= 3]
    diffs = [float(m.split("DIFF: ")[1]) for m in messages if m.startswith("DIFF: ")][1:]  # erste Dauer ist riesig (Legacy)
    sent = bytes(received).split()
    print("frames:", frames)
    print("frame_dauer_s: median=%.3f max=%.3f" % (statistics.median(diffs), max(diffs)))
    print("aktor: %d Kommandos, davon 1: %d, 0: %d" % (len(sent), sent.count(b"1"), sent.count(b"0")))
    print("frames_mit_detektion:", sum(1 for m in messages if re.match(r"Detections: [1-9]", m)))
    for t in LEGACY_MESSAGE_TYPES:
        print("meldungstyp %-16s %s" % (t, "ja" if any(m.startswith(t) for m in messages) else "FEHLT"))
    print("log:", log_path)


if __name__ == "__main__":
    main()
