import subprocess
import sys

import pytest

from hba.cli import build_parser

FLAGS = ["-v", "-S", "-s", "-c", "-d", "-m", "-e", "-t", "-b", "-p"]


def test_defaults_match_baseline():
    args = build_parser().parse_args([])
    assert args.video is False and args.stream is False and args.save is False
    assert args.conf == 0.4
    assert args.device == "cpu"
    assert args.model == "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
    assert args.exposure == "1"
    assert args.time == "700"
    assert args.brightness is None
    assert args.path == "/mnt/hba-stick/HBA/"


def test_long_options_and_values():
    args = build_parser().parse_args(
        ["--video", "--stream", "--save", "--conf", "0.55", "--device", "0", "--model", "m.pt",
         "--exposure", "3", "--time", "1200", "--brightness", "50", "--path", "/data/hba/"]
    )
    assert args.video and args.stream and args.save
    assert (args.conf, args.device, args.model) == (0.55, "0", "m.pt")
    assert (args.exposure, args.time, args.brightness, args.path) == ("3", "1200", "50", "/data/hba/")


def test_help_lists_all_ten_flags():
    out = subprocess.run([sys.executable, "-m", "hba", "--help"], capture_output=True, text=True, check=True).stdout
    for flag in FLAGS:
        assert flag in out, flag
    assert len(FLAGS) == 10


def test_unknown_flag_is_rejected():
    result = subprocess.run([sys.executable, "-m", "hba", "--unbekannt"], capture_output=True, text=True)
    assert result.returncode == 2
