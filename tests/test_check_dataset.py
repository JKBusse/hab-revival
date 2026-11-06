"""Prüfroutine für den Trainingsdatensatz: ein Test je Szenario der Spec `training-data`."""

import importlib.util
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location("check_dataset", os.path.join(ROOT, "tools", "check_dataset.py"))
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)

GOOD = "1 0.5 0.5 0.1 0.2\n"


def make(tmp_path, train_files=None, names="['back', 'front']", valid_files=None):
    """Legt einen kleinen Datensatz an. `train_files`: {Name: Labelinhalt oder None (kein Label)}."""
    (tmp_path / "data.yaml").write_text(f"nc: 2\nnames: {names}\n")
    for split, files in (("train", train_files or {}), ("valid", valid_files or {}), ("test", {})):
        (tmp_path / split / "images").mkdir(parents=True)
        (tmp_path / split / "labels").mkdir(parents=True)
        for stem, label in files.items():
            (tmp_path / split / "images" / f"{stem}.png").write_bytes(b"x")
            if label is not None:
                (tmp_path / split / "labels" / f"{stem}.txt").write_text(label)
    return str(tmp_path)


def test_clean_dataset_has_no_violations(tmp_path):
    ds = make(tmp_path, {"a": GOOD, "OFF1": ""})
    assert cd.check_dataset(ds) == []


def test_image_without_label_is_a_violation(tmp_path):
    ds = make(tmp_path, {"a": GOOD, "b": None})
    violations = cd.check_dataset(ds)
    assert len(violations) == 1 and "train/images/b.png" in violations[0] and "keine Label-Datei" in violations[0]


def test_intentional_negative_with_prefix_off_is_fine(tmp_path):
    assert cd.check_dataset(make(tmp_path, {"OFF123": ""})) == []


def test_empty_label_without_prefix_is_a_violation(tmp_path):
    violations = cd.check_dataset(make(tmp_path, {"a": ""}))
    assert len(violations) == 1 and "train/labels/a.txt" in violations[0] and "OFF" in violations[0]


def test_whitespace_only_label_counts_as_empty(tmp_path):
    assert len(cd.check_dataset(make(tmp_path, {"a": "\n  \n"}))) == 1


def test_label_without_image_is_a_violation(tmp_path):
    ds = make(tmp_path, {"a": GOOD})
    (tmp_path / "train" / "labels" / "verwaist.txt").write_text(GOOD)
    violations = cd.check_dataset(ds)
    assert len(violations) == 1 and "verwaist.txt" in violations[0] and "ohne Bild" in violations[0]


def test_unknown_class_index_is_a_violation(tmp_path):
    violations = cd.check_dataset(make(tmp_path, {"a": "2 0.5 0.5 0.1 0.1\n"}))
    assert any("Klassenindex 2" in v for v in violations)


def test_capitalised_class_names_in_data_yaml_are_a_violation(tmp_path):
    violations = cd.check_dataset(make(tmp_path, {"a": GOOD}, names="['Back', 'Front']"))
    assert len(violations) == 1 and "data.yaml" in violations[0]


def test_wrong_class_order_is_a_violation(tmp_path):
    assert any("data.yaml" in v for v in cd.check_dataset(make(tmp_path, {"a": GOOD}, names="['front', 'back']")))


def test_missing_data_yaml_is_a_violation(tmp_path):
    ds = make(tmp_path, {"a": GOOD})
    os.remove(tmp_path / "data.yaml")
    assert any("data.yaml: fehlt" in v for v in cd.check_dataset(ds))


@pytest.mark.parametrize(
    "line, fragment",
    [
        ("1 0.5 0.5 1.4 0.1", "außerhalb 0 bis 1"),  # Breite 1,4
        ("1 -0.1 0.5 0.1 0.1", "außerhalb 0 bis 1"),
        ("1 0.5 0.5 0.1", "erwartet 5 Werte"),
        ("1 0.5 0.5 0.1 0.1 0.9", "erwartet 5 Werte"),
        ("x 0.5 0.5 0.1 0.1", "keine ganze Zahl"),
        ("1 0.5 abc 0.1 0.1", "kein Zahlenwert"),
    ],
)
def test_malformed_label_lines_are_violations(tmp_path, line, fragment):
    violations = cd.check_dataset(make(tmp_path, {"a": line + "\n"}))
    assert any(fragment in v and "train/labels/a.txt" in v for v in violations), violations


def test_each_bad_line_is_reported_with_its_line_number(tmp_path):
    violations = cd.check_dataset(make(tmp_path, {"a": GOOD + "1 2 0.5 0.1 0.1\n" + GOOD + "9 0.5 0.5 0.1 0.1\n"}))
    assert any("Zeile 2" in v for v in violations) and any("Zeile 4" in v for v in violations)


def test_by_default_only_train_is_checked(tmp_path):
    ds = make(tmp_path, {"a": GOOD}, valid_files={"v": None})  # valid hat ein Bild ohne Label
    assert cd.check_dataset(ds) == []
    assert len(cd.check_dataset(ds, splits=("train", "valid"))) == 1


def test_exit_code_and_message_name_the_file(tmp_path, capsys):
    ds = make(tmp_path, {"a": GOOD, "b": None})
    assert cd.main([ds]) == 1
    assert "train/images/b.png" in capsys.readouterr().out
    clean = tmp_path / "sauber"
    clean.mkdir()
    assert cd.main([make(clean, {"a": GOOD})]) == 0


# --- Prüfsummen von valid und test ------------------------------------------------------------

def test_checksums_are_stable_and_detect_changes(tmp_path):
    ds = make(tmp_path, {"a": GOOD}, valid_files={"v": GOOD})
    manifest = str(tmp_path / "m.sha256")
    assert cd.write_checksums(ds, manifest) == 2  # v.png und v.txt
    assert cd.verify_checksums(ds, manifest) == []
    assert cd.main([ds, "--verify-checksums", manifest]) == 0

    (tmp_path / "valid" / "labels" / "v.txt").write_text("0 0.1 0.1 0.1 0.1\n")  # Inhalt verändert
    (tmp_path / "valid" / "images" / "neu.png").write_bytes(b"y")  # neu
    os.remove(tmp_path / "valid" / "images" / "v.png")  # fehlt
    problems = cd.verify_checksums(ds, manifest)
    assert any("v.txt" in p and "verändert" in p for p in problems)
    assert any("neu.png" in p and "neu hinzugekommen" in p for p in problems)
    assert any("v.png" in p and "fehlt" in p for p in problems)
    assert cd.main([ds, "--verify-checksums", manifest]) == 1


def test_train_changes_do_not_affect_the_frozen_checksums(tmp_path):
    ds = make(tmp_path, {"a": GOOD}, valid_files={"v": GOOD})
    manifest = str(tmp_path / "m.sha256")
    cd.write_checksums(ds, manifest)
    (tmp_path / "train" / "labels" / "a.txt").write_text("0 0.2 0.2 0.2 0.2\n")
    assert cd.verify_checksums(ds, manifest) == []


def test_dot_files_such_as_ds_store_are_ignored(tmp_path):
    ds = make(tmp_path, {"a": GOOD}, valid_files={"v": GOOD})
    manifest = str(tmp_path / "m.sha256")
    (tmp_path / "valid" / ".DS_Store").write_bytes(b"1")
    assert cd.write_checksums(ds, manifest) == 2
    (tmp_path / "valid" / ".DS_Store").write_bytes(b"2")  # der Finder ändert sie
    assert cd.verify_checksums(ds, manifest) == []
