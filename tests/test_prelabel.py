import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location("prelabel", os.path.join(ROOT, "tools", "prelabel.py"))
pl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pl)


def make(tmp_path):
    for sub in ("images", "labels"):
        (tmp_path / "train" / sub).mkdir(parents=True)
    for stem, has_label in (("roh1", False), ("roh2", False), ("fertig", True)):
        (tmp_path / "train" / "images" / f"{stem}.png").write_bytes(b"x")
        if has_label:
            (tmp_path / "train" / "labels" / f"{stem}.txt").write_text("1 0.5 0.5 0.1 0.1\n")
    return str(tmp_path)


def test_only_images_without_label_are_selected(tmp_path):
    names = [os.path.basename(p) for p in pl.unlabeled_images(make(tmp_path))]
    assert names == ["roh1.png", "roh2.png"]


def test_one_label_file_per_image_empty_when_nothing_is_seen(tmp_path):
    ds = make(tmp_path)
    out = tmp_path / "prelabel"

    def predict(path):
        return [(1, 0.5, 0.25, 0.1, 0.2), (0, 0.1, 0.1, 0.05, 0.05)] if path.endswith("roh1.png") else []

    counts = pl.write_prelabels(pl.unlabeled_images(ds), predict, str(out))
    assert counts == {"roh1": 2, "roh2": 0}
    assert (out / "roh1.txt").read_text().splitlines() == ["1 0.500000 0.250000 0.100000 0.200000", "0 0.100000 0.100000 0.050000 0.050000"]
    assert (out / "roh2.txt").read_text() == ""
    assert sorted(os.listdir(out)) == ["roh1.txt", "roh2.txt"]


def test_output_never_goes_into_the_training_set(tmp_path):
    ds = make(tmp_path)
    before = sorted(os.listdir(tmp_path / "train" / "labels"))
    pl.write_prelabels(pl.unlabeled_images(ds), lambda p: [(1, 0.5, 0.5, 0.1, 0.1)], str(tmp_path / "prelabel"))
    assert sorted(os.listdir(tmp_path / "train" / "labels")) == before


def test_default_confidence_is_lower_than_in_operation():
    assert pl.DEFAULT_CONF == 0.25 < 0.4


def test_module_imports_without_torch():
    import subprocess
    import sys

    code = ("import sys, importlib.util;"
            f"s=importlib.util.spec_from_file_location('p', {os.path.join(ROOT, 'tools', 'prelabel.py')!r});"
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m);"
            "print(','.join(x for x in ('torch','ultralytics') if x in sys.modules))")
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""
