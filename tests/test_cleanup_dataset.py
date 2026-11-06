import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cd, cl = load("check_dataset"), load("cleanup_dataset")
GOOD = "1 0.5 0.5 0.1 0.2\n"


def make(tmp_path):
    (tmp_path / "data.yaml").write_text("nc: 2\nnames: ['back', 'front']\n")
    for split in ("train", "valid", "test"):
        (tmp_path / split / "images").mkdir(parents=True)
        (tmp_path / split / "labels").mkdir(parents=True)

    def add(split, stem, label, ext=".png"):
        (tmp_path / split / "images" / (stem + ext)).write_bytes(b"x")
        if label is not None:
            (tmp_path / split / "labels" / (stem + ".txt")).write_text(label)

    add("train", "auto", GOOD)
    add("train", "OFF1", "")  # bewusstes Negativ, bleibt
    add("train", "NOR5_png.rf.abc", "", ext=".jpg")  # leeres Label ohne OFF: wird markiert
    (tmp_path / "train" / "labels" / "verwaist.txt").write_text(GOOD)  # Label ohne Bild
    add("train", "roh", None)  # Bild ohne Label: bleibt (wird später geprüft)
    add("valid", "v", "")  # valid wird nie angefasst
    return str(tmp_path)


def test_dry_run_changes_nothing(tmp_path, capsys):
    ds = make(tmp_path)
    before = sorted(str(p) for p in tmp_path.rglob("*"))
    assert cl.main([ds, "--log", str(tmp_path / "log.md")]) == 0
    assert sorted(str(p) for p in tmp_path.rglob("*")) == before
    assert "Probelauf" in capsys.readouterr().out and not (tmp_path / "log.md").exists()


def test_plan_finds_exactly_the_orphan_and_the_unmarked_negative(tmp_path):
    ds = make(tmp_path)
    plan = cl.plan(ds)
    assert {(a["aktion"], a["datei"]) for a in plan} == {
        ("entfernt", "train/labels/verwaist.txt"),
        ("umbenannt", "train/*/NOR5_png.rf.abc.*"),
    }


def test_apply_removes_orphans_and_marks_negatives_for_image_and_label(tmp_path):
    ds = make(tmp_path)
    log = tmp_path / "log.md"
    assert cl.main([ds, "--apply", "--log", str(log)]) == 0
    assert not (tmp_path / "train" / "labels" / "verwaist.txt").exists()
    assert (tmp_path / "train" / "images" / "OFF_NOR5_png.rf.abc.jpg").exists()
    assert (tmp_path / "train" / "labels" / "OFF_NOR5_png.rf.abc.txt").exists()
    assert not (tmp_path / "train" / "images" / "NOR5_png.rf.abc.jpg").exists()
    # nur die Bilder ohne Label bleiben als Verstoß übrig
    assert cd.check_dataset(ds) == ["train/images/roh.png: keine Label-Datei"]
    # valid unberührt
    assert (tmp_path / "valid" / "images" / "v.png").exists() and (tmp_path / "valid" / "labels" / "v.txt").exists()


def test_log_lists_every_change_with_file_action_reason_and_date(tmp_path):
    ds = make(tmp_path)
    log = tmp_path / "log.md"
    cl.append_log(str(log), cl.plan(ds), today="2026-11-06")
    text = log.read_text()
    assert text.startswith("# Änderungsprotokoll")
    assert "| 2026-11-06 | `train/labels/verwaist.txt` | entfernt | Label ohne Bild |" in text
    assert "NOR5_png.rf.abc" in text and "umbenannt" in text and "bewusstes Negativ" in text


def test_second_run_finds_nothing_to_do(tmp_path):
    ds = make(tmp_path)
    cl.main([ds, "--apply", "--log", str(tmp_path / "log.md")])
    assert cl.plan(ds) == []


def test_log_is_appended_not_overwritten(tmp_path):
    log = tmp_path / "log.md"
    cl.append_log(str(log), [{"aktion": "entfernt", "datei": "train/labels/a.txt", "grund": "x"}], today="2026-11-06")
    cl.append_log(str(log), [{"aktion": "entfernt", "datei": "train/labels/b.txt", "grund": "y"}], today="2026-11-07")
    text = log.read_text()
    assert text.count("# Änderungsprotokoll") == 1 and "a.txt" in text and "b.txt" in text
