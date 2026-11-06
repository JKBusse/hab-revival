import os
import pty
import select
import subprocess
import sys
import textwrap
import time

import pytest

from hba.actuator import ActuatorLink
from hba.lifecycle import Lifecycle


# --- In-Process: Idempotenz und Zeitverhalten ------------------------------------------

class CountingActuator:
    def __init__(self):
        self.closed = 0

    def set_status(self, status):
        pass

    def close(self):
        self.closed += 1


def test_shutdown_is_idempotent():
    actuator = CountingActuator()
    life = Lifecycle(logger=__import__("logging").getLogger("t"), actuator=actuator, close_windows=lambda: None)
    life.shutdown()
    life.shutdown()
    assert actuator.closed == 1


def test_shutdown_sends_zero_exactly_once_on_a_pty():
    master, slave = pty.openpty()
    try:
        link = ActuatorLink(port=os.ttyname(slave), tick=5.0)  # Takt lang: nur Weckrufe und Abschluss senden
        link.set_status(1)
        time.sleep(0.15)
        life = Lifecycle(logger=__import__("logging").getLogger("t"), actuator=link, close_windows=lambda: None)
        before = _drain(master)
        life.shutdown()
        life.shutdown()
        after = _drain(master)
        assert b"1" in before.split()
        assert after.split() == [b"0"]  # genau ein Abschlusskommando
    finally:
        os.close(master)
        os.close(slave)


def _drain(master, timeout=0.4):
    data, end = b"", time.time() + timeout
    while time.time() < end:
        if select.select([master], [], [], 0.05)[0]:
            data += os.read(master, 4096)
    return data


def test_shutdown_with_blocking_port_takes_at_most_two_seconds():
    import threading

    class Blocking:
        def __init__(self):
            self.release = threading.Event()

        def write(self, data):
            self.release.wait(30)

        def flush(self):
            self.release.wait(30)

        def close(self):
            pass

    fake = Blocking()
    link = ActuatorLink(serial_factory=lambda: fake)
    link.set_status(1)
    time.sleep(0.1)
    life = Lifecycle(logger=__import__("logging").getLogger("t"), actuator=link, close_windows=lambda: None)
    start = time.time()
    life.shutdown()
    assert time.time() - start <= 2.0
    fake.release.set()


# --- Subprozess: Signale und Exceptions --------------------------------------------------

def run_child(tmp_path, trigger):
    master, slave = pty.openpty()
    script = textwrap.dedent(
        """
        import os, signal, sys, time
        from hba import monitor
        from hba.actuator import ActuatorLink
        from hba.lifecycle import Lifecycle
        logger = monitor.setup_logger({log_dir!r}, "t")
        link = ActuatorLink(port={port!r}, logger=logger)
        life = Lifecycle(logger, actuator=link, close_windows=lambda: None)
        life.install()
        link.set_status(1)
        time.sleep(0.15)
        """
    ).format(log_dir=str(tmp_path), port=os.ttyname(slave)) + textwrap.dedent(trigger)
    try:
        result = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True, timeout=30)
        sent = _drain(master, 0.3).split()
    finally:
        os.close(master)
        os.close(slave)
    return result, sent, (tmp_path / "t.log").read_text()


@pytest.mark.parametrize(
    "trigger, marker",
    [
        ("os.kill(os.getpid(), signal.SIGTERM)\ntime.sleep(5)\n", "Manual end SIGTERM"),
        ("os.kill(os.getpid(), signal.SIGINT)\ntime.sleep(5)\n", "Manual end CTR-C"),
        ("life.end()\n", "---END---"),  # entspricht der Taste c
    ],
)
def test_controlled_end_sends_zero_and_exits_with_code_0(tmp_path, trigger, marker):
    result, sent, log = run_child(tmp_path, trigger)
    assert result.returncode == 0
    assert b"1" in sent and sent[-1] == b"0"
    assert marker in log
    assert "---END---" in log and "---END---" in result.stdout


def test_unhandled_exception_sends_zero_and_exits_with_nonzero_code(tmp_path):
    result, sent, log = run_child(tmp_path, "raise ValueError('kaputt')\n")
    assert result.returncode != 0
    assert b"1" in sent and sent[-1] == b"0"
    assert "Unhandled exception" in log and "ValueError: kaputt" in log
    assert "---END---" in log


def test_normal_interpreter_exit_also_sends_zero(tmp_path):
    result, sent, _ = run_child(tmp_path, "sys.exit(0)\n")  # nur atexit greift
    assert result.returncode == 0
    assert b"1" in sent and sent[-1] == b"0"
