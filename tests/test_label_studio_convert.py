import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


y2l, l2y = load("yolo_to_ls"), load("ls_to_yolo")

LINES = ["1 0.568750 0.405469 0.022656 0.031250", "0 0.250000 0.600000 0.100000 0.200000", "1 0.999000 0.001000 0.002000 0.002000"]


@pytest.mark.parametrize("line", LINES)
def test_single_line_round_trip_is_exact_to_six_digits(line):
    result = y2l.yolo_line_to_result(line, 640, 640)
    back = y2l.result_to_yolo_line(result)
    for a, b in zip(line.split(), back.split()):
        assert float(a) == pytest.approx(float(b), abs=2e-6)
    assert back.split()[0] == line.split()[0]


def test_percent_coordinates_use_the_top_left_corner():
    r = y2l.yolo_line_to_result("1 0.5 0.5 0.2 0.4", 640, 640)["value"]
    assert (r["x"], r["y"], r["width"], r["height"]) == (40.0, 30.0, 20.0, 40.0)
    assert r["rectanglelabels"] == ["front"]
    assert y2l.yolo_line_to_result("0 0.5 0.5 0.2 0.4", 640, 640)["value"]["rectanglelabels"] == ["back"]


def make_folder(tmp_path):
    images, labels = tmp_path / "images", tmp_path / "labels"
    images.mkdir()
    labels.mkdir()
    for stem, content in (("a", LINES[0] + "\n" + LINES[1] + "\n"), ("b", ""), ("c", None)):
        (images / f"{stem}.png").write_bytes(b"x")
        if content is not None:
            (labels / f"{stem}.txt").write_text(content)
    (images / "notiz.txt").write_text("kein Bild")
    return str(images), str(labels)


def test_only_images_with_a_prelabel_become_tasks(tmp_path):
    images, labels = make_folder(tmp_path)
    tasks = y2l.build_tasks(images, labels, root=str(tmp_path))
    assert [t["data"]["name"] for t in tasks] == ["a.png", "b.png"]  # c.png hat kein Vorlabel, notiz.txt ist kein Bild
    assert len(tasks[0]["predictions"][0]["result"]) == 2
    assert tasks[1]["predictions"][0]["result"] == []  # Vorlabel leer: Modell sah kein Fahrzeug
    assert tasks[0]["data"]["image"] == "/data/local-files/?d=images/a.png"


def test_all_images_can_be_requested_and_then_have_no_predictions_without_prelabel(tmp_path):
    images, labels = make_folder(tmp_path)
    tasks = y2l.build_tasks(images, labels, root=str(tmp_path), only_prelabeled=False)
    assert [t["data"]["name"] for t in tasks] == ["a.png", "b.png", "c.png"]
    assert "predictions" not in tasks[2]


def test_without_a_prelabel_folder_every_image_is_a_task(tmp_path):
    images, _ = make_folder(tmp_path)
    tasks = y2l.build_tasks(images, None, root=str(tmp_path))
    assert [t["data"]["name"] for t in tasks] == ["a.png", "b.png", "c.png"]
    assert all("predictions" not in t for t in tasks)


def test_full_round_trip_yolo_to_label_studio_to_yolo(tmp_path):
    images, labels = make_folder(tmp_path)
    tasks = y2l.build_tasks(images, labels, root=str(tmp_path))
    # Der Mensch bestätigt die Vorschläge unverändert: Annotation = Vorhersage
    for task in tasks:
        if "predictions" in task:
            task["annotations"] = [{"was_cancelled": False, "result": task["predictions"][0]["result"]}]
    out = tmp_path / "out"
    decisions = l2y.convert(tasks, str(out))
    assert decisions == {"a": "geprüft", "b": "geprüft"}
    original = [l.split() for l in (tmp_path / "labels" / "a.txt").read_text().splitlines()]
    result = [l.split() for l in (out / "a.txt").read_text().splitlines()]
    assert len(original) == len(result) == 2
    for o, r in zip(original, result):
        assert o[0] == r[0]
        assert [float(v) for v in o[1:]] == pytest.approx([float(v) for v in r[1:]], abs=2e-6)
    assert (out / "b.txt").read_text() == ""  # bewusstes Negativ bleibt leer


def test_skip_means_discarded_and_no_label_is_written(tmp_path):
    task = {"data": {"image": "/data/local-files/?d=images/x.png", "name": "x.png"},
            "annotations": [{"was_cancelled": True, "result": []}]}
    assert l2y.decide(task) == ("verworfen", None)
    l2y.convert([task], str(tmp_path / "o"))
    assert not (tmp_path / "o" / "x.txt").exists()
    assert "x\tverworfen" in (tmp_path / "o" / "entscheidungen.tsv").read_text()


def test_human_correction_wins_over_the_prediction():
    corrected = y2l.yolo_line_to_result("1 0.3 0.3 0.1 0.1", 640, 640)
    task = {"data": {"image": "/data/local-files/?d=images/x.png", "name": "x.png"},
            "predictions": [{"result": [y2l.yolo_line_to_result("0 0.9 0.9 0.1 0.1", 640, 640)]}],
            "annotations": [{"was_cancelled": False, "result": [corrected]}]}
    decision, lines = l2y.decide(task)
    assert decision == "geprüft" and lines[0].startswith("1 0.300000 0.300000")


def test_undecided_tasks_make_the_script_fail(tmp_path, capsys):
    export = tmp_path / "e.json"
    export.write_text(json.dumps([{"data": {"image": "/data/local-files/?d=i/x.png", "name": "x.png"}}]))
    assert l2y.main([str(export), str(tmp_path / "o")]) == 1
    assert "offen: x" in capsys.readouterr().out


def test_last_submitted_annotation_counts_and_skips_are_ignored():
    first = y2l.yolo_line_to_result("0 0.1 0.1 0.1 0.1", 640, 640)
    last = y2l.yolo_line_to_result("1 0.8 0.8 0.1 0.1", 640, 640)
    task = {"data": {"image": "x", "name": "x.png"}, "annotations": [
        {"was_cancelled": False, "result": [first]},
        {"was_cancelled": False, "result": [last]},
        {"was_cancelled": True, "result": []},
    ]}
    assert l2y.decide(task)[1][0].startswith("1 0.800000")


def test_label_studio_config_lists_exactly_the_two_classes():
    import xml.etree.ElementTree as ET

    tree = ET.parse(os.path.join(ROOT, "tools", "label_studio_config.xml"))
    labels = [e.get("value") for e in tree.iter("Label")]
    assert labels == ["back", "front"]
