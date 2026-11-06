"""Kalibrier-Fenster: Darstellung (ohne Display) und Aufruf (Smoke-Tests ohne Fenster)."""

import os
import subprocess
import sys

import cv2
import numpy as np
import pytest

from hba import exit_codes
from hba.calibrate import LEFT_WIDTH, RIGHT_SIZE, STATUS_HEIGHT, render, view_scales
from hba.calibration import CalibrationState, Rect
from hba.config import Config


def run(*args, cwd=None):
    return subprocess.run([sys.executable, "-m", "hba.calibrate", *args], capture_output=True, text=True,
                          timeout=60, cwd=cwd)


@pytest.fixture
def test_image(tmp_path):
    rng = np.random.default_rng(5)
    path = tmp_path / "bild.png"
    cv2.imwrite(str(path), rng.integers(40, 200, size=(1080, 1920, 3), dtype=np.uint8))
    return str(path)


FRAME = np.random.default_rng(5).integers(40, 200, size=(1080, 1920, 3), dtype=np.uint8)
BASE = Config.defaults()


def px(canvas, x, y):
    return tuple(int(v) for v in canvas[y, x])


def test_default_state_shows_the_960_by_426_crop():
    state = CalibrationState.from_config(BASE)
    assert (state.crop.width, state.crop.height) == (960, 426)


def test_render_has_both_views_and_a_status_bar():
    canvas = render(CalibrationState.from_config(BASE), FRAME, BASE)
    left_t, _ = view_scales(1920)
    left_height = round(1080 * left_t.scale)
    assert canvas.shape == (max(left_height, RIGHT_SIZE) + STATUS_HEIGHT, LEFT_WIDTH + RIGHT_SIZE, 3)


def test_crop_rectangle_is_drawn_where_the_state_says():
    state = CalibrationState.from_config(BASE)
    left_t, _ = view_scales(1920)
    canvas = render(state, FRAME, BASE)
    x0, y0 = left_t.to_display(state.crop.x0, state.crop.y0)
    mid_y = left_t.to_display(0, (state.crop.y0 + state.crop.y1) // 2)[1]
    assert px(canvas, x0, mid_y) == (0, 200, 0)  # linke Kante
    moved = CalibrationState.from_config(BASE)
    moved.crop = Rect(200, 212, 1160, 638)
    canvas2 = render(moved, FRAME, BASE)
    assert px(canvas2, left_t.to_display(200, 0)[0], mid_y) == (0, 200, 0)
    assert px(canvas2, x0, mid_y) != (0, 200, 0)


def test_min_top_line_is_drawn_in_the_crop_view_at_the_filter_scale():
    state = CalibrationState.from_config(BASE)
    _, right_t = view_scales(1920)
    canvas = render(state, FRAME, BASE)
    y = right_t.to_display(0, 160)[1]
    assert px(canvas, LEFT_WIDTH + RIGHT_SIZE - 3, y) == (0, 255, 255)
    state.min_top = 300
    assert px(render(state, FRAME, BASE), LEFT_WIDTH + RIGHT_SIZE - 3, right_t.to_display(0, 300)[1]) == (0, 255, 255)


def test_area_above_the_line_is_darkened():
    state = CalibrationState.from_config(BASE)
    _, right_t = view_scales(1920)
    canvas = render(state, FRAME, BASE)
    above = canvas[right_t.to_display(0, 40)[1], LEFT_WIDTH + 300].astype(int).sum()
    below = canvas[right_t.to_display(0, 400)[1], LEFT_WIDTH + 300].astype(int).sum()
    assert above < below  # oberhalb von min_top abgedunkelt (nicht relevant)


def test_right_view_is_what_the_pipeline_sees():
    from hba.capture import prepare_frame

    state = CalibrationState.from_config(BASE)
    state.crop = Rect(300, 100, 1300, 600)
    _, model_input = prepare_frame(FRAME, state.to_config(BASE))
    expected = cv2.resize(model_input, (RIGHT_SIZE, RIGHT_SIZE), interpolation=cv2.INTER_AREA)
    canvas = render(state, FRAME, BASE)
    # Bereich ohne Linie, Marke und Text: mitten im Bild unterhalb der Marke
    rows, cols = slice(RIGHT_SIZE - 120, RIGHT_SIZE - 60), slice(200, 300)
    assert np.array_equal(canvas[rows, LEFT_WIDTH + cols.start:LEFT_WIDTH + cols.stop], expected[rows, cols])


# --- Aufruf --------------------------------------------------------------------------------------

def test_help_works():
    result = run("--help")
    assert result.returncode == 0 and "--image" in result.stdout and "--camera" in result.stdout


def test_a_source_is_required():
    assert run().returncode == 2


def test_missing_image_reports_a_clear_error_and_exit_code_2(tmp_path):
    result = run("--image", str(tmp_path / "fehlt.png"))
    assert result.returncode == exit_codes.EXIT_CONFIG
    assert "Bild nicht lesbar" in result.stderr


def test_missing_config_file_is_an_error(tmp_path, test_image):
    result = run("--image", test_image, "--config", str(tmp_path / "gibt-es-nicht.yaml"))
    assert result.returncode == exit_codes.EXIT_CONFIG and "nicht gefunden" in result.stderr


def test_invalid_config_is_reported(tmp_path, test_image):
    cfg = tmp_path / "kaputt.yaml"
    cfg.write_text("decision:\n  hold_secs: 5\n")
    result = run("--image", test_image, "--config", str(cfg))
    assert result.returncode == exit_codes.EXIT_CONFIG and "decision.hold_secs" in result.stderr


def test_render_to_writes_an_image_without_opening_a_window(tmp_path, test_image):
    out = tmp_path / "out.png"
    result = run("--image", test_image, "--render-to", str(out), cwd=str(tmp_path))
    assert result.returncode == 0, result.stderr
    canvas = cv2.imread(str(out))
    assert canvas.shape[1] == LEFT_WIDTH + RIGHT_SIZE and canvas.shape[0] > STATUS_HEIGHT


def test_other_image_sizes_are_scaled_with_a_hint(tmp_path):
    small = tmp_path / "klein.png"
    cv2.imwrite(str(small), np.zeros((640, 640, 3), dtype=np.uint8))
    out = tmp_path / "out.png"
    result = run("--image", str(small), "--render-to", str(out), cwd=str(tmp_path))
    assert result.returncode == 0 and "skaliert" in result.stderr


def test_tool_needs_no_gpu_model_or_serial_port():
    code = (
        "import sys, hba.calibrate;"
        "print(','.join(m for m in ('torch','ultralytics','serial','hba.actuator','hba.detect') if m in sys.modules))"
    )
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""
