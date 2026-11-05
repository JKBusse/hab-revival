import logging
import os
import pty
import select

import pytest

from hba.actuator import SerialActuator
from hba.ports import Actuator


@pytest.fixture
def pty_pair():
    master, slave = pty.openpty()
    yield master, os.ttyname(slave)
    os.close(master)
    os.close(slave)


def read_available(master, timeout=0.5):
    data = b""
    while select.select([master], [], [], timeout)[0]:
        data += os.read(master, 1024)
        timeout = 0.05
    return data


def test_correct_bytes_arrive(pty_pair):
    master, name = pty_pair
    actuator = SerialActuator(port=name)
    assert actuator.enabled
    actuator.set_status(1)
    actuator.set_status(0)
    actuator.set_status(1)
    assert read_available(master) == b"1\n0\n1\n"
    actuator.close()


def test_satisfies_actuator_port(pty_pair):
    _, name = pty_pair
    actuator = SerialActuator(port=name)
    assert isinstance(actuator, Actuator)
    actuator.close()


def test_missing_adapter_runs_without_actuator(tmp_path, caplog):
    logger = logging.getLogger("HBA-test-actuator")
    with caplog.at_level(logging.INFO, logger=logger.name):
        actuator = SerialActuator(port=str(tmp_path / "ttyUSB0"), logger=logger)
    assert not actuator.enabled
    actuator.set_status(1)  # darf nicht werfen
    actuator.close()
    assert "configure_serial_connection: ERROR!" in caplog.text


def test_ok_is_logged_when_adapter_present(pty_pair, caplog):
    _, name = pty_pair
    logger = logging.getLogger("HBA-test-actuator-ok")
    with caplog.at_level(logging.INFO, logger=logger.name):
        actuator = SerialActuator(port=name, logger=logger)
    assert "configure_serial_connection: OK" in caplog.text
    actuator.close()


def test_write_error_disables_actuator_permanently(pty_pair, capsys):
    master, name = pty_pair
    actuator = SerialActuator(port=name)

    class Broken:
        def write(self, data):
            raise OSError("Adapter abgezogen")

        def close(self):
            pass

    actuator._serial = Broken()
    actuator.set_status(1)
    assert not actuator.enabled
    assert "Serial not Possible!" in capsys.readouterr().out
    # weitere Kommandos werden nicht mehr gesendet, auch nicht nach Ersatz des Ports
    class Recording:
        sent = []

        def write(self, data):
            self.sent.append(data)

        def close(self):
            pass

    rec = Recording()
    actuator._serial = rec
    actuator.set_status(0)
    assert rec.sent == []


def test_close_sends_no_final_command(pty_pair):
    master, name = pty_pair
    actuator = SerialActuator(port=name)
    actuator.set_status(1)
    actuator.close()
    assert read_available(master) == b"1\n"
