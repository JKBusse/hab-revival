import logging
import os

import pytest

from hba.config import (
    DEFAULTS, Config, ConfigError, describe, load_config, resolve_config_path,
)

ROOT = os.path.dirname(os.path.dirname(__file__))
EXAMPLE = os.path.join(ROOT, "config", "hba.example.yaml")


def write(tmp_path, text, name="hba.yaml"):
    path = tmp_path / name
    path.write_text(text)
    return str(path)


# --- 1.1 Standardwerte = Legacy ---------------------------------------------------------------

def test_defaults_are_the_legacy_values():
    c = Config.defaults()
    assert (c.camera.device, c.camera.width, c.camera.height) == (0, 1920, 1080)
    assert c.camera.rotate_180 is True
    assert (c.camera.exposure, c.camera.exposure_time, c.camera.brightness) == (1, 700, None)
    assert (c.image.hood_rows, c.image.crop_rows, c.image.crop_cols) == (850, (212, 638), (400, 1360))
    assert c.detection.model == "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
    assert (c.detection.device, c.detection.conf) == ("0", 0.4)
    assert (c.relevance.max_width, c.relevance.min_top) == (500, 160)
    assert c.decision.hold_seconds == 3
    assert (c.serial.port, c.serial.baudrate) == ("/dev/ttyUSB0", 9600)
    assert c.recording.path == "/mnt/hba-stick/HBA/"
    assert c.recording.sample_probability == pytest.approx(1 / 99)
    assert c.recording.detection_probability == pytest.approx(9 / 99)
    assert c.recording.max_files == 1000
    assert (c.output.video, c.output.stream, c.output.save) == (False, False, False)


def test_start_without_file_gives_exactly_the_defaults():
    loaded = load_config(None, {})
    assert loaded.config == Config.defaults()
    assert loaded.warnings == [] and loaded.path is None
    assert set(loaded.sources.values()) == {"Standard"}


# --- 1.2 Laden, Vorrang, Pfadauflösung ---------------------------------------------------------

def test_no_file_anywhere_means_only_defaults(tmp_path):
    assert resolve_config_path(None, cwd=str(tmp_path)) is None


def test_hba_yaml_in_working_directory_is_used(tmp_path):
    path = write(tmp_path, "detection:\n  conf: 0.5\n")
    assert resolve_config_path(None, cwd=str(tmp_path)) == path


def test_explicit_path_wins_over_working_directory(tmp_path):
    write(tmp_path, "detection:\n  conf: 0.5\n")
    other = write(tmp_path, "detection:\n  conf: 0.6\n", name="andere.yaml")
    assert resolve_config_path(other, cwd=str(tmp_path)) == other


def test_explicit_file_missing_is_an_error(tmp_path):
    with pytest.raises(ConfigError) as info:
        resolve_config_path(str(tmp_path / "gibt-es-nicht.yaml"))
    assert "nicht gefunden" in info.value.errors[0]


def test_file_values_override_defaults(tmp_path):
    loaded = load_config(write(tmp_path, "serial:\n  port: /dev/ttyUSB7\n"), {})
    assert loaded.config.serial.port == "/dev/ttyUSB7"
    assert loaded.config.serial.baudrate == 9600
    assert loaded.sources["serial.port"] == "Datei" and loaded.sources["serial.baudrate"] == "Standard"


def test_flag_beats_file(tmp_path):
    path = write(tmp_path, "detection:\n  conf: 0.5\n")
    assert load_config(path, {}).config.detection.conf == 0.5
    loaded = load_config(path, {"conf": 0.6})
    assert loaded.config.detection.conf == 0.6
    assert loaded.sources["detection.conf"] == "Flag"


def test_flags_that_were_not_given_do_not_override(tmp_path):
    path = write(tmp_path, "detection:\n  conf: 0.5\n  device: cpu\n")
    loaded = load_config(path, {"conf": None, "device": None, "video": None})
    assert loaded.config.detection.conf == 0.5 and loaded.config.detection.device == "cpu"


def test_text_flags_for_camera_values_are_converted():
    loaded = load_config(None, {"exposure": "3", "time": "1200", "brightness": "50"})
    assert (loaded.config.camera.exposure, loaded.config.camera.exposure_time,
            loaded.config.camera.brightness) == (3, 1200, 50)


def test_non_numeric_text_flag_is_an_error():
    with pytest.raises(ConfigError) as info:
        load_config(None, {"time": "viel"})
    assert "--time" in info.value.errors[0]


def test_empty_file_is_fine(tmp_path):
    assert load_config(write(tmp_path, ""), {}).config == Config.defaults()


def test_broken_yaml_is_an_error(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, "camera: [unclosed"), {})


# --- 1.3 Prüfung beim Start -----------------------------------------------------------------------

def errors_of(tmp_path, text):
    with pytest.raises(ConfigError) as info:
        load_config(write(tmp_path, text), {})
    return info.value.errors


def test_typo_in_key_names_the_key(tmp_path):
    errors = errors_of(tmp_path, "decision:\n  hold_secs: 5\n")
    assert any("decision.hold_secs" in e for e in errors)


def test_unknown_section_is_rejected(tmp_path):
    assert any("kamera" in e for e in errors_of(tmp_path, "kamera:\n  device: 1\n"))


def test_crop_beyond_the_image_is_rejected(tmp_path):
    errors = errors_of(tmp_path, "image:\n  crop_cols: [400, 2000]\n")
    assert any("crop_cols" in e and "hinaus" in e for e in errors)


def test_crop_rows_must_stay_above_the_hood_line(tmp_path):
    assert any("crop_rows" in e for e in errors_of(tmp_path, "image:\n  crop_rows: [212, 900]\n"))


def test_crop_start_must_be_before_end(tmp_path):
    assert any("crop_rows" in e for e in errors_of(tmp_path, "image:\n  crop_rows: [500, 300]\n"))


def test_wrong_type_is_rejected(tmp_path):
    assert any("detection.conf" in e for e in errors_of(tmp_path, 'detection:\n  conf: "hoch"\n'))
    assert any("camera.rotate_180" in e for e in errors_of(tmp_path, "camera:\n  rotate_180: 1\n"))


@pytest.mark.parametrize(
    "text, key",
    [
        ("detection:\n  conf: 1.5\n", "detection.conf"),
        ("recording:\n  sample_probability: 2\n", "recording.sample_probability"),
        ("recording:\n  detection_probability: -0.1\n", "recording.detection_probability"),
        ("recording:\n  max_files: 0\n", "recording.max_files"),
        ("camera:\n  exposure: 2\n", "camera.exposure"),
        ("camera:\n  exposure_time: 9000\n", "camera.exposure_time"),
        ("camera:\n  brightness: 500\n", "camera.brightness"),
        ("relevance:\n  max_width: 0\n", "relevance.max_width"),
        ("relevance:\n  min_top: 640\n", "relevance.min_top"),
        ("serial:\n  baudrate: 0\n", "serial.baudrate"),
    ],
)
def test_out_of_range_values_are_rejected(tmp_path, text, key):
    assert any(key in e for e in errors_of(tmp_path, text))


def test_all_errors_are_reported_together(tmp_path):
    errors = errors_of(tmp_path, "decision:\n  hold_secs: 5\ndetection:\n  conf: 9\nkamera: {}\n")
    assert len(errors) == 3


def test_error_message_names_the_source_of_the_bad_value(tmp_path):
    errors = errors_of(tmp_path, "detection:\n  conf: 9\n")
    assert "Datei" in errors[0]
    with pytest.raises(ConfigError) as info:
        load_config(None, {"conf": 9.0})
    assert "Flag" in info.value.errors[0]


# --- 1.4 Haltezeit -----------------------------------------------------------------------------

def test_hold_time_below_three_seconds_warns_but_starts(tmp_path):
    loaded = load_config(write(tmp_path, "decision:\n  hold_seconds: 1\n"), {})
    assert loaded.config.decision.hold_seconds == 1
    assert len(loaded.warnings) == 1 and "Haltezeit" in loaded.warnings[0]


@pytest.mark.parametrize("value", [3, 5, 10.5])
def test_hold_time_of_three_seconds_or_more_does_not_warn(tmp_path, value):
    assert load_config(write(tmp_path, f"decision:\n  hold_seconds: {value}\n"), {}).warnings == []


@pytest.mark.parametrize("value", [0, -1, -0.5])
def test_hold_time_zero_or_negative_is_an_error(tmp_path, value):
    assert any("hold_seconds" in e for e in errors_of(tmp_path, f"decision:\n  hold_seconds: {value}\n"))


# --- 1.5 Effektive Werte mit Quelle loggen ---------------------------------------------------------

def test_describe_lists_every_value_with_its_source(tmp_path):
    loaded = load_config(write(tmp_path, "detection:\n  conf: 0.5\n  device: cpu\n"), {"device": "0", "video": True})
    lines = describe(loaded)
    assert len(lines) == sum(len(v) for v in DEFAULTS.values())
    text = "\n".join(lines)
    assert "detection.conf = 0.5 (Datei)" in text
    assert "detection.device = '0' (Flag)" in text
    assert "output.video = True (Flag)" in text
    assert "serial.port = '/dev/ttyUSB0' (Standard)" in text


# --- 1.6 Beispiel-Datei ---------------------------------------------------------------------------------

def test_example_file_gives_exactly_the_built_in_defaults():
    loaded = load_config(EXAMPLE, {})
    assert loaded.config == Config.defaults()
    assert loaded.warnings == []
    assert set(loaded.sources.values()) == {"Datei"}  # jeder Schlüssel steht in der Beispiel-Datei


def test_example_file_has_no_key_missing_from_the_defaults():
    from ruamel.yaml import YAML

    data = YAML(typ="safe").load(open(EXAMPLE))
    assert {s: set(v) for s, v in data.items()} == {s: set(v) for s, v in DEFAULTS.items()}


def test_cross_checks_still_run_when_another_error_exists(tmp_path):
    errors = errors_of(tmp_path, "decision:\n  hold_secs: 5\nimage:\n  crop_cols: [400, 2000]\n")
    assert any("decision.hold_secs" in e for e in errors)
    assert any("crop_cols" in e and "hinaus" in e for e in errors)


def test_cross_check_is_skipped_when_the_value_itself_is_invalid(tmp_path):
    errors = errors_of(tmp_path, 'image:\n  crop_cols: "viel"\n')
    assert len(errors) == 1 and "image.crop_cols" in errors[0]  # keine Folgefehler
