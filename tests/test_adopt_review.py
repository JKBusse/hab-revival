import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ad = load("adopt_review")
BOX = "1 0.5 0.5 0.1 0.2\n"


def make(tmp_path, extra_label=False):
    ds = tmp_path / "ds"
    for split in ("train", "valid"):
        (ds / split / "images").mkdir(parents=True)
        (ds / split / "labels").mkdir(parents=True)
    for stem in ("a", "b", "c", "alt"):
        (ds / "train" / "images" / (stem + ".png")).write_bytes(b"x")
    (ds / "train" / "labels" / "alt.txt").write_text(BOX)  # schon gelabelt, nicht Teil der Prüfung
    (ds / "valid" / "images" / "v.png").write_bytes(b"v")
    if extra_label:
        (ds / "train" / "labels" / "a.txt").write_text(BOX)
    rev = tmp_path / "rev"
    rev.mkdir()
    (rev / "a.txt").write_text(BOX)
    (rev / "b.txt").write_text("")
    (rev / "entscheidungen.tsv").write_text("a\tgeprüft\nb\tgeprüft\nc\tverworfen\n", encoding="utf-8")
    return str(ds), str(rev)


def test_dry_run_changes_nothing(tmp_path):
    ds, rev = make(tmp_path)
    before = sorted(str(p) for p in tmp_path.rglob("*"))
    assert ad.main([ds, rev, "--log", str(tmp_path / "log.md")]) == 0
    assert sorted(str(p) for p in tmp_path.rglob("*")) == before
    assert not (tmp_path / "log.md").exists()


def test_apply_labels_marks_negatives_and_removes_discarded(tmp_path):
    ds, rev = make(tmp_path)
    log = tmp_path / "log.md"
    assert ad.main([ds, rev, "--apply", "--log", str(log)]) == 0
    train = tmp_path / "ds" / "train"
    assert (train / "labels" / "a.txt").read_text() == BOX
    assert (train / "images" / "OFF_b.png").exists() and not (train / "images" / "b.png").exists()
    assert (train / "labels" / "OFF_b.txt").read_text() == ""
    assert not (train / "images" / "c.png").exists()
    assert (train / "images" / "alt.png").exists()  # unberührt
    text = log.read_text(encoding="utf-8")
    assert text.count("\n| 20") == 3  # eine Zeile je Entscheidung
    assert "verworfen" in text and "bewusstes Negativ" in text and "1 Rahmen" in text


def test_existing_label_aborts_before_any_change(tmp_path, capsys):
    ds, rev = make(tmp_path, extra_label=True)
    before = sorted(str(p) for p in tmp_path.rglob("*"))
    assert ad.main([ds, rev, "--apply", "--log", str(tmp_path / "log.md")]) == 1
    assert sorted(str(p) for p in tmp_path.rglob("*")) == before
    assert "a: hat schon ein Label" in capsys.readouterr().err


def test_unknown_image_aborts(tmp_path, capsys):
    ds, rev = make(tmp_path)
    with open(os.path.join(rev, "entscheidungen.tsv"), "a", encoding="utf-8") as handle:
        handle.write("zz\tgeprüft\n")
    assert ad.main([ds, rev, "--apply", "--log", str(tmp_path / "log.md")]) == 1
    assert "zz: Bild nicht in train/images" in capsys.readouterr().err


def test_valid_split_is_never_touched(tmp_path):
    ds, rev = make(tmp_path)
    ad.main([ds, rev, "--apply", "--log", str(tmp_path / "log.md")])
    assert (tmp_path / "ds" / "valid" / "images" / "v.png").read_bytes() == b"v"
