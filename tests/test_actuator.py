import logging
import os
import pty
import select
import threading
import time

import pytest

import hba.actuator as actuator_module
from hba.actuator import ActuatorLink
from hba.ports import Actuator


# --- Hilfen -------------------------------------------------------------------

def make_pty():
    master, slave = pty.openpty()
    return master, slave, os.ttyname(slave)


def read_for(master, seconds):
    """Liest `seconds` lang alles, was ankommt, und liefert [(zeit, bytes)]."""
    chunks, end = [], time.time() + seconds
    while time.time() < end:
        if select.select([master], [], [], 0.02)[0]:
            chunks.append((time.time(), os.read(master, 4096)))
    return chunks


def tokens(chunks):
    return b"".join(c for _, c in chunks).split()


def read_until(master, predicate, timeout=3.0):
    data, end = b"", time.time() + timeout
    while time.time() < end:
        if select.select([master], [], [], 0.02)[0]:
            data += os.read(master, 4096)
            if predicate(data.split()):
                return data.split()
    return data.split()


@pytest.fixture
def pty_pair():
    master, slave, name = make_pty()
    yield master, name
    for fd in (master, slave):
        try:
            os.close(fd)
        except OSError:
            pass


@pytest.fixture
def links():
    created = []
    yield created
    for link in created:
        link.close()


def make_link(links, *args, **kwargs):
    link = ActuatorLink(*args, **kwargs)
    links.append(link)
    return link


# --- Standardwerte und Verbindungsparameter -----------------------------------

def test_defaults_match_design():
    assert (actuator_module.PORT, actuator_module.BAUDRATE) == ("/dev/ttyUSB0", 9600)
    assert actuator_module.TICK_SECONDS == 0.2
    assert actuator_module.STALE_SECONDS == 0.5
    assert actuator_module.RECONNECT_SECONDS == 2.0
    assert actuator_module.REMIND_SECONDS == 30.0
    assert actuator_module.WRITE_TIMEOUT == 0.5


def test_serial_parameters(monkeypatch):
    import serial

    seen = {}

    class Spy:
        def __init__(self, **kwargs):
            seen.update(kwargs)

        def write(self, data):
            pass

        def close(self):
            pass

    monkeypatch.setattr(serial, "Serial", Spy)
    link = ActuatorLink(port="/dev/ttyUSB0", autostart=False)
    link.close()
    assert seen["port"] == "/dev/ttyUSB0"
    assert seen["baudrate"] == 9600
    assert seen["bytesize"] == 8
    assert seen["stopbits"] == serial.STOPBITS_ONE
    assert seen["timeout"] == 2
    assert seen["write_timeout"] == 0.5


# --- 2.1 Sender und Heartbeat -----------------------------------------------------

def test_status_arrives_and_gaps_stay_below_half_a_second(pty_pair, links):
    master, name = pty_pair
    link = make_link(links, port=name)
    assert isinstance(link, Actuator)
    read_for(master, 0.08)  # das anfängliche Heartbeat-0 (Fail-Safe-Startwert) verwerfen
    stop = threading.Event()

    def frames():  # etwa 8 Frames pro Sekunde
        while not stop.is_set():
            link.set_status(1)
            time.sleep(0.12)

    thread = threading.Thread(target=frames, daemon=True)
    thread.start()
    chunks = read_for(master, 1.5)
    stop.set()
    thread.join()
    assert chunks and set(tokens(chunks)) == {b"1"}
    times = [t for t, _ in chunks]
    assert max(b - a for a, b in zip(times, times[1:])) <= 0.5


def test_heartbeat_continues_without_new_decision_for_status_zero(pty_pair, links):
    master, name = pty_pair
    link = make_link(links, port=name)
    link.set_status(0)
    chunks = read_for(master, 1.0)
    times = [t for t, _ in chunks]
    assert set(tokens(chunks)) == {b"0"}
    assert max(b - a for a, b in zip(times, times[1:])) <= 0.5


def test_dimming_is_sent_without_waiting_for_the_heartbeat_tick(pty_pair, links):
    master, name = pty_pair
    link = make_link(links, port=name, tick=5.0)  # Takt so lang, dass nur der Weckruf zählt
    link.set_status(1)
    assert read_until(master, lambda t: b"1" in t, 1.0)
    start = time.time()
    link.set_status(0)
    assert read_until(master, lambda t: t and t[-1] == b"0", 1.0)[-1] == b"0"
    assert time.time() - start < 0.2


# --- 2.2 Veraltete Entscheidung ------------------------------------------------------

def test_stale_decision_sends_zero_and_never_one_again(pty_pair, links):
    master, name = pty_pair
    link = make_link(links, port=name)
    read_for(master, 0.08)  # das anfängliche Heartbeat-0 (Fail-Safe-Startwert) verwerfen
    link.set_status(1)
    start = time.time()
    chunks = read_for(master, 1.4)
    seq = tokens(chunks)
    assert seq[0] == b"1"
    first_zero = next(i for i, t in enumerate(seq) if t == b"0")
    assert all(t == b"0" for t in seq[first_zero:])  # danach nie wieder 1
    # die erste 0 kommt nach 0,5 s Staleness plus höchstens einen Takt
    zero_time = next(t for t, c in chunks if b"0" in c)
    assert 0.45 <= zero_time - start <= 0.9


# --- 2.3 Wiederverbindung --------------------------------------------------------------

def test_reconnect_after_adapter_is_unplugged_and_replugged(tmp_path, caplog, links):
    caplog.set_level(logging.INFO)
    link_path = tmp_path / "tty"
    master_a, slave_a, name_a = make_pty()
    os.symlink(name_a, link_path)
    logger = logging.getLogger("HBA-test-reconnect")
    link = make_link(links, port=str(link_path), logger=logger, tick=0.05, reconnect_every=0.2)
    link.set_status(1)
    assert read_until(master_a, lambda t: b"1" in t, 1.0)

    os.close(master_a)  # Adapter abgezogen
    os.close(slave_a)
    deadline = time.time() + 2
    while link.connected and time.time() < deadline:
        link.set_status(1)
        time.sleep(0.05)
    assert not link.connected

    master_b, slave_b, name_b = make_pty()  # Adapter wieder eingesteckt (anderer Gerätename)
    os.unlink(link_path)
    os.symlink(name_b, link_path)
    try:
        deadline = time.time() + 5
        received = []
        while time.time() < deadline and b"1" not in received:
            link.set_status(1)
            received = read_until(master_b, lambda t: b"1" in t, 0.2)
        assert b"1" in received
    finally:
        os.close(master_b)
        os.close(slave_b)
    errors = [r for r in caplog.records if r.levelno == logging.ERROR and r.name == logger.name]
    assert len(errors) == 1 and "lost" in errors[0].getMessage()
    assert any("restored" in r.getMessage() for r in caplog.records if r.levelno == logging.INFO)


def test_error_is_logged_once_with_reminders_every_30_seconds(caplog):
    logger = logging.getLogger("HBA-test-reminder")
    now = [0.0]

    def failing():
        raise OSError("kein Adapter")

    caplog.set_level(logging.INFO, logger=logger.name)
    link = ActuatorLink(logger=logger, serial_factory=failing, clock=lambda: now[0], autostart=False)
    for second in range(2, 66, 2):  # 65 Sekunden lang alle 2 s ein Tick
        now[0] = float(second)
        link._tick()
    errors = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert errors[0] == "configure_serial_connection: ERROR!"
    assert len(errors) == 3  # Start plus Erinnerungen bei 30 s und 60 s
    assert all("still lost" in e for e in errors[1:])
    link.close()


# --- 2.4 Start ohne Adapter -------------------------------------------------------------

def test_start_without_adapter_does_not_raise_and_connects_when_device_appears(tmp_path, caplog, links):
    caplog.set_level(logging.INFO)
    logger = logging.getLogger("HBA-test-nostart")
    path = tmp_path / "ttyUSB0"
    link = make_link(links, port=str(path), logger=logger, tick=0.05, reconnect_every=0.2)
    assert not link.connected
    assert any(r.getMessage() == "configure_serial_connection: ERROR!" for r in caplog.records)
    link.set_status(1)  # darf nicht werfen, Status gilt als 0

    master, slave, name = make_pty()
    os.symlink(name, path)  # Gerät erscheint
    try:
        deadline = time.time() + 5
        received = []
        while time.time() < deadline and not received:
            link.set_status(1)
            received = read_until(master, lambda t: len(t) > 0, 0.2)
        assert link.connected and b"1" in received
    finally:
        os.close(master)
        os.close(slave)


def test_ok_is_logged_when_adapter_present(pty_pair, caplog, links):
    caplog.set_level(logging.INFO)
    _, name = pty_pair
    make_link(links, port=name, logger=logging.getLogger("HBA-test-ok"))
    assert any(r.getMessage() == "configure_serial_connection: OK" for r in caplog.records)


# --- 2.5 Sender-Thread gegen eigene Fehler ------------------------------------------------

def test_sender_thread_survives_internal_errors(pty_pair, caplog, links):
    master, name = pty_pair
    logger = logging.getLogger("HBA-test-thread")
    link = make_link(links, port=name, logger=logger, tick=0.02, autostart=False)
    original, calls = link._tick, []

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("eingespeist")
        original()

    link._tick = flaky
    link._thread.start()
    link.set_status(1)
    assert read_until(master, lambda t: b"1" in t, 2.0)  # läuft nach dem Fehler weiter
    assert link._thread.is_alive()
    assert any("eingespeist" in (r.exc_text or "") or r.exc_info for r in caplog.records if r.levelno == logging.ERROR)


# --- Beenden (close) -------------------------------------------------------------------------

def test_close_sends_zero_after_status_one(pty_pair):
    master, name = pty_pair
    link = ActuatorLink(port=name)
    link.set_status(1)
    assert read_until(master, lambda t: b"1" in t, 1.0)
    link.close()
    seq = read_until(master, lambda t: b"0" in t, 1.0)
    assert seq[-1] == b"0"


def test_close_is_idempotent_and_set_status_after_close_is_ignored(pty_pair):
    master, name = pty_pair
    link = ActuatorLink(port=name)
    link.close()
    first = read_for(master, 0.3)
    link.close()
    link.set_status(1)
    second = read_for(master, 0.3)
    assert tokens(first).count(b"0") >= 1
    assert second == []  # nichts mehr nach dem zweiten close und set_status


class BlockingSerial:
    """Schnittstelle, deren Schreiben nie zurückkehrt (hängender Adapter)."""

    def __init__(self):
        self.release = threading.Event()

    def write(self, data):
        self.release.wait(30)

    def flush(self):
        self.release.wait(30)

    def close(self):
        pass


def test_close_with_hanging_adapter_takes_at_most_two_seconds(links):
    fake = BlockingSerial()
    link = ActuatorLink(serial_factory=lambda: fake, autostart=True)
    link.set_status(1)
    time.sleep(0.1)  # Sender hängt jetzt im Schreiben
    start = time.time()
    link.close()
    assert time.time() - start <= 2.0
    fake.release.set()


def test_close_without_connection_returns_immediately():
    def failing():
        raise OSError("weg")

    link = ActuatorLink(serial_factory=failing, autostart=False)
    start = time.time()
    link.close()
    assert time.time() - start < 0.2
