import os
import stat

import pytest

from hba.calibration import (
    CalibrationState, MouseController, Rect, ViewTransform, hit_handle, move_rect, resize_rect,
    save, validate_overrides, write_overrides,
)
from hba.config import Config, ConfigError, load_config

ROOT = os.path.dirname(os.path.dirname(__file__))
EXAMPLE = os.path.join(ROOT, "config", "hba.example.yaml")


# --- 3.1 Geometrie ---------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dx, dy, expected",
    [
        (10, 20, Rect(110, 70, 210, 170)),
        (-500, 0, Rect(0, 50, 100, 150)),  # links am Rand
        (0, -500, Rect(100, 0, 200, 100)),  # oben am Rand
        (5000, 0, Rect(900, 50, 1000, 150)),  # rechts am Rand (max_x 1000)
        (0, 5000, Rect(100, 500, 200, 600)),  # unten am Rand (max_y 600)
    ],
)
def test_move_rect_keeps_its_size_and_stays_inside(dx, dy, expected):
    assert move_rect(Rect(100, 50, 200, 150), dx, dy, 1000, 600) == expected


@pytest.mark.parametrize(
    "handle, x, y, expected",
    [
        ("br", 300, 250, Rect(100, 50, 300, 250)),
        ("tl", 50, 20, Rect(50, 20, 200, 150)),
        ("tr", 400, 10, Rect(100, 10, 400, 150)),
        ("bl", 20, 400, Rect(20, 50, 200, 400)),
        ("br", 5000, 5000, Rect(100, 50, 1000, 600)),  # an den Rand geklemmt
        ("tl", 190, 140, Rect(100 + 80, 50 + 80, 200, 150)),  # nie kleiner als 20
    ],
)
def test_resize_rect_by_corner(handle, x, y, expected):
    assert resize_rect(Rect(100, 50, 200, 150), handle, x, y, 1000, 600) == expected


@pytest.mark.parametrize(
    "x, y, expected",
    [(100, 50, "tl"), (203, 52, "tr"), (98, 148, "bl"), (200, 150, "br"), (150, 100, "move"), (500, 500, None)],
)
def test_hit_handle(x, y, expected):
    assert hit_handle(Rect(100, 50, 200, 150), x, y, tolerance=5) == expected


def test_view_transform_round_trip():
    t = ViewTransform(0.5)
    assert t.to_image(480, 213) == (960, 426)
    assert t.to_display(960, 426) == (480, 213)
    # Eine verkleinerte Ansicht verliert Auflösung: der Rundweg trifft auf 1/Maßstab Pixel genau.
    for x in (0, 1, 333, 1919):
        back_x, back_y = t.to_image(*t.to_display(x, x))
        assert abs(back_x - x) <= 1 / t.scale and abs(back_y - x) <= 1 / t.scale
    assert ViewTransform(1.0).to_image(*ViewTransform(1.0).to_display(7, 9)) == (7, 9)  # ohne Verkleinerung exakt


def state(**kw):
    base = dict(crop=Rect(400, 212, 1360, 638), min_top=160, max_width=500, hood_rows=850, frame_width=1920, frame_height=1080)
    base.update(kw)
    return CalibrationState(**base)


def controller(st):
    return MouseController(st, ViewTransform(0.5), ViewTransform(1.0), left_width=960)


def test_default_state_is_the_legacy_crop():
    st = CalibrationState.from_config(Config.defaults())
    assert st.crop.width == 960 and st.crop.height == 426  # 960x426
    assert (st.min_top, st.max_width) == (160, 500)


def test_mouse_moves_the_crop():
    st = state()
    c = controller(st)
    c.on_down(480, 212)  # Mitte des Ausschnitts in der Anzeige (Maßstab 0,5)
    c.on_move(480 + 50, 212 + 25)  # 100 x 50 Bildpixel
    c.on_up()
    assert st.crop == Rect(500, 262, 1460, 688)


def test_mouse_resizes_a_corner():
    st = state()
    c = controller(st)
    c.on_down(680, 319)  # Ecke unten rechts (1360, 638) * 0,5
    c.on_move(600, 300)  # (1200, 600)
    c.on_up()
    assert st.crop == Rect(400, 212, 1200, 600)


def test_crop_cannot_leave_the_area_above_the_hood_line():
    st = state()
    c = controller(st)
    c.on_down(480, 212)
    c.on_move(480, 2000)
    c.on_up()
    assert st.crop.y1 <= 850 and st.crop.height == 426


def test_mouse_drags_the_min_top_line_in_the_crop_view():
    st = state()
    c = controller(st)
    c.on_down(960 + 300, 160)  # auf der Linie
    c.on_move(960 + 300, 100)
    c.on_up()
    assert st.min_top == 100


def test_mouse_drags_the_max_width_marker():
    st = state()
    c = controller(st)
    c.on_down(960 + 500, c.bar_y)
    c.on_move(960 + 380, c.bar_y)
    c.on_up()
    assert st.max_width == 380


def test_click_elsewhere_changes_nothing():
    st = state()
    before = (st.crop, st.min_top, st.max_width)
    c = controller(st)
    c.on_down(10, 10)
    c.on_move(300, 300)
    c.on_up()
    c.on_down(960 + 50, 400)
    c.on_move(960 + 60, 410)
    assert (st.crop, st.min_top, st.max_width) == before


def test_state_to_config_uses_the_same_crop_as_the_pipeline():
    from hba.capture import prepare_frame
    import numpy as np

    st = state(crop=Rect(300, 100, 1300, 600))
    crop, model_input = prepare_frame(np.zeros((1080, 1920, 3), dtype=np.uint8), st.to_config(Config.defaults()))
    assert crop.shape == (500, 1000, 3) and model_input.shape == (640, 640, 3)


# --- 3.2 Prüfen und Schreiben ----------------------------------------------------------------------

ORIGINAL = """\
# Meine Konfiguration (Kommentar oben)
camera:
  device: 0            # /dev/video<device>
  rotate_180: true

image:
  hood_rows: 850                # Zeilen ab hier werden verworfen
  crop_rows: [212, 638]         # Erkennungsausschnitt, Zeilen von bis
  crop_cols: [400, 1360]        # Erkennungsausschnitt, Spalten von bis

relevance:             # Aktive Fläche
  max_width: 500       # Box muss schmaler sein
  min_top: 160         # obere Kante

detection:
  device: "0"          # GPU-Index
"""


def write_file(tmp_path, text=ORIGINAL):
    path = tmp_path / "hba.yaml"
    path.write_text(text)
    return str(path)


def test_round_trip_changes_only_the_edited_values(tmp_path):
    path = write_file(tmp_path)
    write_overrides(path, {"image": {"crop_cols": [300, 1300]}, "relevance": {"min_top": 100}})
    expected = ORIGINAL.replace("[400, 1360]", "[300, 1300]").replace("min_top: 160", "min_top: 100")
    assert open(path).read() == expected  # Kommentare, Reihenfolge, Leerzeilen, Anführungszeichen unverändert


def test_write_without_changes_leaves_the_bytes_identical(tmp_path):
    path = write_file(tmp_path)
    write_overrides(path, {"image": {"crop_rows": [212, 638], "crop_cols": [400, 1360]}, "relevance": {"max_width": 500, "min_top": 160}})
    assert open(path).read() == ORIGINAL


def test_missing_keys_and_sections_are_added(tmp_path):
    path = write_file(tmp_path, "camera:\n  device: 1  # meine Kamera\n")
    write_overrides(path, {"image": {"crop_cols": [300, 1300]}, "relevance": {"min_top": 100}})
    loaded = load_config(path, {})
    assert loaded.config.camera.device == 1
    assert loaded.config.image.crop_cols == (300, 1300) and loaded.config.relevance.min_top == 100
    assert "# meine Kamera" in open(path).read()


def test_new_file_is_created(tmp_path):
    path = str(tmp_path / "neu.yaml")
    write_overrides(path, {"relevance": {"min_top": 100, "max_width": 400}})
    loaded = load_config(path, {})
    assert (loaded.config.relevance.min_top, loaded.config.relevance.max_width) == (100, 400)


def test_no_temporary_files_are_left_and_permissions_stay(tmp_path):
    path = write_file(tmp_path)
    os.chmod(path, 0o640)
    write_overrides(path, {"relevance": {"min_top": 100}})
    assert os.listdir(tmp_path) == ["hba.yaml"]
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o640


def test_example_file_round_trip_only_touches_the_edited_lines(tmp_path):
    path = str(tmp_path / "ex.yaml")
    text = open(EXAMPLE).read()
    open(path, "w").write(text)
    write_overrides(path, {"image": {"crop_cols": [300, 1300]}, "relevance": {"min_top": 100}})
    old, new = text.splitlines(), open(path).read().splitlines()
    assert len(old) == len(new)
    changed = [(a, b) for a, b in zip(old, new) if a != b]
    assert len(changed) == 2
    assert all(("crop_cols" in a and "[300, 1300]" in b) or ("min_top" in a and "100" in b) for a, b in changed)


def test_valid_values_are_saved_with_all_other_keys_unchanged(tmp_path):
    path = write_file(tmp_path)
    st = state(crop=Rect(300, 100, 1300, 600), min_top=120)
    loaded = save(path, st)
    after = load_config(path, {}).config
    assert after.image.crop_cols == (300, 1300) and after.image.crop_rows == (100, 600)
    assert after.relevance.min_top == 120 and after.relevance.max_width == 500
    assert after.camera.device == 0 and after.detection.device == "0"
    assert loaded.config.relevance.min_top == 120


def test_invalid_values_write_nothing_and_name_the_reason(tmp_path):
    path = write_file(tmp_path)
    bad = state(crop=Rect(400, 212, 2000, 638))  # ragt über das Bild hinaus
    with pytest.raises(ConfigError) as info:
        save(path, bad)
    assert any("crop_cols" in e and "hinaus" in e for e in info.value.errors)
    assert open(path).read() == ORIGINAL  # nichts geschrieben
    assert os.listdir(tmp_path) == ["hba.yaml"]


def test_validate_overrides_uses_the_start_up_checks(tmp_path):
    path = write_file(tmp_path)
    assert validate_overrides(path, {"relevance": {"min_top": 100}}).config.relevance.min_top == 100
    with pytest.raises(ConfigError):
        validate_overrides(path, {"relevance": {"min_top": 700}})
