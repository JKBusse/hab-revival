"""Tests für den Change gpu-required: Start-Prüfung, CUDA-Fehler, Watchdog, Exit-Codes."""

import logging
import os
import pty
import select
import subprocess
import sys
import textwrap
import threading
import time

import numpy as np
import pytest

from fakes import FakeActuator, FakeCamera, FakeClock, FakeDetector
from hba import exit_codes, monitor
from hba.app import Pipeline, WarmUpTimeout
from hba.detect import GpuUnavailable
from hba.recorder import Recorder
from hba.startup import create_detector_or_exit, warm_up_or_exit
from hba.watchdog import WATCHDOG_SECONDS, Watchdog

FRAME = np.zeros((1080, 1920, 3), dtype=np.uint8)
LOGGER = logging.getLogger("HBA-test-gpu")
TESTS_DIR = os.path.dirname(__file__)


class NoRandom:
    def randrange(self, a, b):
        return 1


class RecordingLifecycle:
    def __init__(self):
        self.calls = []

    def end(self, code=0):
        self.calls.append(("end", code))

    def hard_exit(self, code, reason):
        self.calls.append(("hard_exit", code))


class BlockingDetector:
    def __init__(self):
        self.release = threading.Event()

    def detect(self, image):
        self.release.wait(30)
        return []


def make_pipeline(tmp_path, detector, camera_frames=3):
    (tmp_path / "log").mkdir(exist_ok=True)
    logger = monitor.setup_logger(str(tmp_path / "log"), "t")
    pipeline = Pipeline(
        FakeCamera([FRAME] * camera_frames), detector, FakeActuator(), FakeClock(),
        Recorder(str(tmp_path), save_all=False, rng=NoRandom()), logger,
    )
    return pipeline


# --- 2.1 Start-Prüfung ------------------------------------------------------------------

def test_no_gpu_ends_with_exit_code_3():
    lifecycle = RecordingLifecycle()

    def no_cuda():
        raise GpuUnavailable("CUDA ist nicht verfügbar")

    create_detector_or_exit(no_cuda, lifecycle, LOGGER)
    assert lifecycle.calls == [("end", exit_codes.EXIT_NO_GPU)]


def test_detector_is_returned_when_gpu_is_fine():
    lifecycle = RecordingLifecycle()
    sentinel = object()
    assert create_detector_or_exit(lambda: sentinel, lifecycle, LOGGER) is sentinel
    assert lifecycle.calls == []


def test_warm_up_that_hangs_ends_hard_with_exit_code_3(tmp_path):
    detector = BlockingDetector()
    pipeline = make_pipeline(tmp_path, detector)
    lifecycle = RecordingLifecycle()
    start = time.time()
    warm_up_or_exit(pipeline, lifecycle, LOGGER, gpu=True, timeout=0.3)
    assert lifecycle.calls == [("hard_exit", exit_codes.EXIT_NO_GPU)]
    assert time.time() - start < 2
    detector.release.set()


def test_warm_up_failure_on_gpu_counts_as_no_gpu(tmp_path):
    class Failing:
        def detect(self, image):
            raise RuntimeError("CUDA error: unspecified launch failure")

    lifecycle = RecordingLifecycle()
    warm_up_or_exit(make_pipeline(tmp_path, Failing()), lifecycle, LOGGER, gpu=True, timeout=5)
    assert lifecycle.calls == [("end", exit_codes.EXIT_NO_GPU)]


def test_warm_up_failure_on_cpu_propagates(tmp_path):
    class Failing:
        def detect(self, image):
            raise ValueError("kaputt")

    with pytest.raises(ValueError):
        warm_up_or_exit(make_pipeline(tmp_path, Failing()), RecordingLifecycle(), LOGGER, gpu=False, timeout=5)


def test_good_warm_up_continues(tmp_path):
    lifecycle = RecordingLifecycle()
    pipeline = make_pipeline(tmp_path, FakeDetector([[]]))
    warm_up_or_exit(pipeline, lifecycle, LOGGER, gpu=True, timeout=5)
    assert lifecycle.calls == []


def test_warm_up_timeout_is_a_gpu_problem():
    assert issubclass(WarmUpTimeout, GpuUnavailable)


def test_default_warm_up_limit_is_30_seconds():
    from hba.app import WARMUP_SECONDS
    assert WARMUP_SECONDS == 30.0


# --- 3.1 CUDA-Fehler im Betrieb -------------------------------------------------------------

def test_cuda_error_in_inference_dims_and_propagates(tmp_path, caplog):
    class CudaFail:
        def __init__(self):
            self.n = 0

        def detect(self, image):
            self.n += 1
            if self.n == 2:
                raise RuntimeError("CUDA error: an illegal memory access was encountered")
            return []

    pipeline = make_pipeline(tmp_path, CudaFail())
    pipeline.logger.propagate = True
    with caplog.at_level(logging.ERROR, logger=pipeline.logger.name):
        with pytest.raises(RuntimeError):
            pipeline.run()
    assert pipeline.actuator.statuses[-1] == 0  # sofort abgeblendet
    assert any("CUDA-Fehler in der Inferenz" in r.getMessage() for r in caplog.records)


# --- 3.2 Watchdog -------------------------------------------------------------------------------

def test_watchdog_default_is_five_seconds():
    assert WATCHDOG_SECONDS == 5.0


def test_watchdog_fires_once_after_the_timeout():
    now, fired = [0.0], []
    dog = Watchdog(on_expire=lambda: fired.append(now[0]), timeout=5.0, clock=lambda: now[0])
    now[0] = 4.9
    assert not dog.check() and fired == []
    now[0] = 5.0
    assert dog.check() and fired == [5.0]
    now[0] = 10.0
    assert not dog.check() and fired == [5.0]  # nur einmal


def test_watchdog_stays_quiet_with_normal_frame_times():
    now, fired = [0.0], []
    dog = Watchdog(on_expire=lambda: fired.append(1), timeout=5.0, clock=lambda: now[0])
    for _ in range(1000):  # Frames mit 0,1 bis 0,2 s
        now[0] += 0.15
        dog.beat()
        assert not dog.check()
    assert fired == []


def test_watchdog_thread_fires_when_beats_stop():
    fired = threading.Event()
    dog = Watchdog(on_expire=fired.set, timeout=0.3, poll=0.02)
    dog.start()
    assert fired.wait(2.0)


def test_watchdog_thread_does_not_fire_while_beating():
    fired = threading.Event()
    dog = Watchdog(on_expire=fired.set, timeout=0.3, poll=0.02)
    dog.start()
    for _ in range(25):
        dog.beat()
        time.sleep(0.04)
    dog.stop()
    assert not fired.is_set()


def test_pipeline_reports_every_finished_frame_to_the_watchdog(tmp_path):
    beats = []
    pipeline = make_pipeline(tmp_path, FakeDetector([[], []]))
    pipeline.heartbeat = lambda: beats.append(1)
    pipeline.step()
    pipeline.step()
    assert len(beats) == 2


# --- Subprozess mit Pseudo-Terminal: 2.2 und 3.3 ---------------------------------------------

def drain(master, seconds=0.3):
    data, end = b"", time.time() + seconds
    while time.time() < end:
        if select.select([master], [], [], 0.05)[0]:
            data += os.read(master, 4096)
    return data


def run_child(tmp_path, body, timeout=60):
    master, slave = pty.openpty()
    script = textwrap.dedent(
        """
        import os, sys, time, signal, threading
        sys.path.insert(0, {tests!r})
        import numpy as np
        from fakes import FakeActuator, FakeCamera, FakeClock
        from hba import exit_codes, monitor
        from hba.actuator import ActuatorLink
        from hba.app import Pipeline
        from hba.detect import GpuUnavailable
        from hba.lifecycle import Lifecycle
        from hba.recorder import Recorder
        from hba.startup import create_detector_or_exit, warm_up_or_exit
        from hba.watchdog import Watchdog
        os.makedirs({log_dir!r} + "/log", exist_ok=True)
        logger = monitor.setup_logger({log_dir!r} + "/log", "t")
        link = ActuatorLink(port={port!r}, logger=logger)
        life = Lifecycle(logger, actuator=link, close_windows=lambda: None)
        life.install()
        FRAME = np.zeros((1080, 1920, 3), dtype=np.uint8)
        class SystemClock:
            def now(self): return time.time()
        class NoRandom:
            def randrange(self, a, b): return 1
        def pipeline_with(detector, **kw):
            return Pipeline(FakeCamera([FRAME] * 10), detector, link, SystemClock(),
                            Recorder({log_dir!r}, save_all=False, rng=NoRandom()), logger, **kw)
        """
    ).format(tests=TESTS_DIR, log_dir=str(tmp_path), port=os.ttyname(slave)) + textwrap.dedent(body)
    start = time.time()
    try:
        result = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True, timeout=timeout)
        result.ended_at = time.time()
        elapsed = result.ended_at - start
        sent = drain(master).split()
    finally:
        os.close(master)
        os.close(slave)
    log_path = tmp_path / "log" / "t.log"
    return result, sent, elapsed, log_path.read_text() if log_path.exists() else ""


def test_no_gpu_at_start_sends_zero_logs_error_and_exits_with_3(tmp_path):
    result, sent, _, log = run_child(
        tmp_path,
        """
        def no_cuda():
            raise GpuUnavailable("CUDA ist nicht verfügbar")
        create_detector_or_exit(no_cuda, life, logger)
        print("DARF NICHT ERREICHT WERDEN")
        """,
    )
    assert result.returncode == exit_codes.EXIT_NO_GPU
    assert "DARF NICHT ERREICHT WERDEN" not in result.stdout
    assert b"0" in sent and b"1" not in sent
    assert "Keine nutzbare GPU" in log and "ERROR" in log


def test_hanging_warm_up_exits_hard_with_3_and_zero_on_the_line(tmp_path):
    result, sent, elapsed, log = run_child(
        tmp_path,
        """
        class Hang:
            def detect(self, image):
                time.sleep(60)
        warm_up_or_exit(pipeline_with(Hang()), life, logger, gpu=True, timeout=1.0)
        print("DARF NICHT ERREICHT WERDEN")
        """,
    )
    assert result.returncode == exit_codes.EXIT_NO_GPU
    assert "DARF NICHT ERREICHT WERDEN" not in result.stdout
    assert elapsed < 15
    assert b"0" in sent and b"1" not in sent
    assert "Keine nutzbare GPU" in log


def test_cuda_error_in_operation_sends_zero_and_exits_with_1(tmp_path):
    result, sent, _, log = run_child(
        tmp_path,
        """
        class Detector:
            n = 0
            def detect(self, image):
                self.n += 1
                if self.n == 3:
                    raise RuntimeError("CUDA error: unspecified launch failure")
                return []
        pipeline = pipeline_with(Detector(), start_seconds=int(time.time()) - 10)  # Status 1 möglich
        pipeline.warm_up()
        pipeline.run()
        """,
    )
    assert result.returncode == exit_codes.EXIT_ERROR
    assert b"1" in sent and sent[-1] == b"0"
    assert "CUDA-Fehler in der Inferenz" in log


def test_hanging_inference_is_ended_by_the_watchdog_within_five_seconds(tmp_path):
    result, sent, elapsed, log = run_child(
        tmp_path,
        """
        class Detector:
            n = 0
            def detect(self, image):
                self.n += 1
                if self.n == 3:
                    print("HANG", time.time(), flush=True)
                    time.sleep(120)
                return []
        dog = Watchdog(on_expire=lambda: life.hard_exit(exit_codes.EXIT_WATCHDOG, "Watchdog: Hauptschleife hängt"))
        pipeline = pipeline_with(Detector(), start_seconds=int(time.time()) - 10, heartbeat=dog.beat)
        pipeline.warm_up()
        dog.start()
        pipeline.run()
        """,
        timeout=90,
    )
    assert result.returncode == exit_codes.EXIT_WATCHDOG
    hang_time = float([l for l in result.stdout.splitlines() if l.startswith("HANG")][0].split()[1])
    # Der Watchdog zählt ab dem letzten fertigen Frame, der unmittelbar vor dem Hänger endet. Er soll
    # nicht früher als nach 5 s auslösen und mit Abfrageintervall (0,1 s) und dem Absenden der `0`
    # (0,15 s) spätestens nach etwa 5,3 s beenden.
    assert 4.9 <= result.ended_at - hang_time <= 5.5
    assert b"1" in sent and sent[-1] == b"0"
    assert "Hauptschleife hängt" in log
