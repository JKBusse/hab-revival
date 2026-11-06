"""Die Unit-Datei im Repo: Schlüsselzeilen und Abwesenheit von Abhängigkeiten (Spec service-supervision)."""

import configparser
import os

import pytest

UNIT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "deploy", "hba.service")


@pytest.fixture(scope="module")
def unit():
    parser = configparser.ConfigParser(strict=False, interpolation=None, comment_prefixes=("#",))
    parser.optionxform = str  # Groß-/Kleinschreibung der Schlüssel erhalten
    parser.read(UNIT, encoding="utf-8")
    return parser


def test_restart_policy(unit):
    assert unit["Service"]["Restart"] == "on-failure"
    assert unit["Service"]["RestartSec"] == "10"
    assert unit["Unit"]["StartLimitIntervalSec"] == "0"  # endlos, keine Sperre


def test_controlled_stop(unit):
    assert unit["Service"]["TimeoutStopSec"] == "5"
    assert unit["Service"]["KillSignal"] == "SIGTERM"


def test_runs_as_jkb_and_starts_at_boot(unit):
    assert unit["Service"]["User"] == "jkb"
    assert unit["Install"]["WantedBy"] == "multi-user.target"


def test_starts_the_package_not_the_legacy_script(unit):
    assert unit["Service"]["ExecStart"].endswith("/.venv/bin/python -m hba")
    assert "yolov8.py" not in unit["Service"]["ExecStart"]


def test_no_dependency_on_the_usb_stick_or_the_network():
    text = open(UNIT, encoding="utf-8").read()
    active = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    for forbidden in ("RequiresMountsFor", "Requires=", "BindsTo=", "After=", "Wants=", "network", "mnt"):
        assert forbidden not in active, forbidden


def test_a_clean_exit_does_not_restart(unit):
    # Restart=on-failure startet bei Exit-Code 0 (gewollter Stopp) nicht neu. Nicht "always"!
    assert unit["Service"]["Restart"] != "always"


def test_documented_legacy_units_are_kept_unchanged_for_reference():
    root = os.path.join(os.path.dirname(UNIT))
    old = open(os.path.join(root, "hba.service.2024")).read()
    assert "ExecStart=/usr/bin/python3 /home/jkb/yolov8.py -d 0" in old and "Restart" not in old
    sensor = open(os.path.join(root, "sensor.service")).read()
    assert "nvidia1.py" in sensor
