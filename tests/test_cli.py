import subprocess
import sys

import pytest

from hba import exit_codes, monitor
from hba.cli import build_parser, load_runtime_config
from hba.config import Config, ConfigError

FLAGS = ["-v", "-S", "-s", "-c", "-d", "-m", "-e", "-t", "-b", "-p"]


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "hba", *args], capture_output=True, text=True, timeout=60)


def test_flags_carry_no_defaults_of_their_own():
    args = build_parser().parse_args([])
    assert all(value is None for key, value in vars(args).items())


def test_effective_defaults_match_baseline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # kein ./hba.yaml
    loaded = load_runtime_config(build_parser().parse_args([]))
    assert loaded.config == Config.defaults()
    c = loaded.config
    assert (c.output.video, c.output.stream, c.output.save) == (False, False, False)
    assert c.detection.conf == 0.4 and c.detection.device == "0"
    assert c.detection.model == "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
    assert (c.camera.exposure, c.camera.exposure_time, c.camera.brightness) == (1, 700, None)
    assert c.recording.path == "/mnt/hba-stick/HBA/"


def test_long_options_and_values(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = build_parser().parse_args(
        ["--video", "--stream", "--save", "--conf", "0.55", "--device", "cpu", "--model", "m.pt",
         "--exposure", "3", "--time", "1200", "--brightness", "50", "--path", "/data/hba/"]
    )
    c = load_runtime_config(args).config
    assert c.output.video and c.output.stream and c.output.save
    assert (c.detection.conf, c.detection.device, c.detection.model) == (0.55, "cpu", "m.pt")
    assert (c.camera.exposure, c.camera.exposure_time, c.camera.brightness) == (3, 1200, 50)
    assert c.recording.path == "/data/hba/"


def test_flag_beats_config_file(tmp_path):
    cfg = tmp_path / "x.yaml"
    cfg.write_text("detection:\n  conf: 0.5\n")
    assert load_runtime_config(build_parser().parse_args(["--config", str(cfg)])).config.detection.conf == 0.5
    both = build_parser().parse_args(["--config", str(cfg), "-c", "0.6"])
    assert load_runtime_config(both).config.detection.conf == 0.6


def test_help_lists_all_flags():
    out = run_cli("--help").stdout
    for flag in FLAGS + ["--config"]:
        assert flag in out, flag
    assert len(FLAGS) == 10


def test_unknown_flag_is_rejected():
    assert run_cli("--unbekannt").returncode == 2


def test_invalid_config_ends_with_exit_code_2_and_names_the_key(tmp_path):
    cfg = tmp_path / "kaputt.yaml"
    cfg.write_text("decision:\n  hold_secs: 5\nimage:\n  crop_cols: [400, 2000]\n")
    result = run_cli("--config", str(cfg), "-p", str(tmp_path))
    assert result.returncode == exit_codes.EXIT_CONFIG
    assert "decision.hold_secs" in result.stderr and "crop_cols" in result.stderr


def test_missing_explicit_config_ends_with_exit_code_2(tmp_path):
    result = run_cli("--config", str(tmp_path / "gibt-es-nicht.yaml"))
    assert result.returncode == exit_codes.EXIT_CONFIG
    assert "nicht gefunden" in result.stderr


def test_non_numeric_flag_ends_with_exit_code_2():
    result = run_cli("--time", "viel")
    assert result.returncode == exit_codes.EXIT_CONFIG


def test_short_hold_time_starts_and_the_warning_is_in_the_log(tmp_path):
    cfg = tmp_path / "kurz.yaml"
    cfg.write_text("decision:\n  hold_seconds: 1\n")
    args = build_parser().parse_args(["--config", str(cfg)])
    loaded = load_runtime_config(args)  # wirft nicht: der Start gelingt
    (tmp_path / "log").mkdir()
    logger = monitor.setup_logger(str(tmp_path / "log"), "t")
    monitor.log_config(logger, loaded)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    text = (tmp_path / "log" / "t.log").read_text()
    assert "WARNING" in text and "Haltezeit" in text
    assert "decision.hold_seconds = 1.0 (Datei)" in text
    assert "detection.conf = 0.4 (Standard)" in text


@pytest.mark.parametrize("value", ["0", "-1"])
def test_hold_time_zero_or_negative_aborts_the_start(tmp_path, value):
    cfg = tmp_path / "null.yaml"
    cfg.write_text(f"decision:\n  hold_seconds: {value}\n")
    with pytest.raises(ConfigError):
        load_runtime_config(build_parser().parse_args(["--config", str(cfg)]))
