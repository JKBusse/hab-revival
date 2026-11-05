import subprocess
import sys
import textwrap

import pytest


def run_script(tmp_path, body):
    script = textwrap.dedent(
        """
        import os, signal, sys
        from hba import monitor
        from hba.lifecycle import Lifecycle
        logger = monitor.setup_logger({log_dir!r}, "t")
        life = Lifecycle(logger, close_windows=lambda: None)
        life.install()
        """
    ).format(log_dir=str(tmp_path)) + textwrap.dedent(body)
    result = subprocess.run([sys.executable, "-I", "-c", script], capture_output=True, text=True, timeout=30)
    return result, (tmp_path / "t.log").read_text()


def test_unhandled_exception_is_logged_and_exits_with_code_0(tmp_path):
    result, log = run_script(tmp_path, "raise ValueError('kaputt')\n")
    assert result.returncode == 0  # Legacy: Exit-Code 0 (wird in fail-safe-shutdown geändert)
    assert "Unhandled exception" in log
    assert "ValueError: kaputt" in log
    assert "---END---" in log
    assert "---END---" in result.stdout


def test_sigint_ends_cleanly(tmp_path):
    result, log = run_script(tmp_path, "os.kill(os.getpid(), signal.SIGINT)\nimport time; time.sleep(5)\n")
    assert result.returncode == 0
    assert "Manual end CTR-C" in log
    assert "---END---" in log


def test_end_prints_marker_and_logs_critical(tmp_path):
    result, log = run_script(tmp_path, "life.end()\n")
    assert result.returncode == 0
    assert "CRITICAL - ---END---" in log
    assert "---END---" in result.stdout
