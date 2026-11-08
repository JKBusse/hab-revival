"""Ergebnis der Bildprüfung (Label Studio) in das Trainingsset übernehmen (Spec `training-data`).

    python tools/adopt_review.py <datensatz> <geprueft-ordner>            # Probelauf
    python tools/adopt_review.py <datensatz> <geprueft-ordner> --apply

`<geprueft-ordner>` ist die Ausgabe von `tools/ls_to_yolo.py` (`<stem>.txt` je geprüftem Bild und
`entscheidungen.tsv`). Je Bild aus der Entscheidungsliste:

  geprüft mit Rahmen    Label wird nach `train/labels/<stem>.txt` geschrieben
  geprüft ohne Rahmen   bewusstes Negativ: Bild und (leeres) Label bekommen das Präfix `OFF_`
  verworfen             Bild wird aus `train/images/` entfernt

Es werden nur Bilder angefasst, die in `train/images/` liegen und noch KEIN Label haben. Alles andere bricht
vor der ersten Änderung ab. Jede Änderung kommt ins Änderungsprotokoll.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("cleanup_dataset", os.path.join(HERE, "cleanup_dataset.py"))
cleanup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cleanup)
check = cleanup.check

REVIEWED, DISCARDED = "geprüft", "verworfen"


class AdoptError(Exception):
    pass


def read_decisions(review_dir: str) -> list[tuple[str, str]]:
    path = os.path.join(review_dir, "entscheidungen.tsv")
    if not os.path.isfile(path):
        raise AdoptError(f"{path} fehlt (Ausgabe von ls_to_yolo.py)")
    rows = []
    for line in open(path, encoding="utf-8").read().splitlines():
        if line.strip():
            stem, decision = line.split("\t")
            if decision not in (REVIEWED, DISCARDED):
                raise AdoptError(f"Unbekannte Entscheidung für {stem}: {decision}")
            rows.append((stem, decision))
    return rows


def plan(dataset: str, review_dir: str) -> list[dict]:
    images = check._stems(os.path.join(dataset, "train", "images"), check.IMAGE_EXTENSIONS)
    labels = check._stems(os.path.join(dataset, "train", "labels"), (".txt",))
    actions, problems = [], []
    for stem, decision in read_decisions(review_dir):
        if stem not in images:
            problems.append(f"{stem}: Bild nicht in train/images")
            continue
        if stem in labels:
            problems.append(f"{stem}: hat schon ein Label (wird nicht überschrieben)")
            continue
        if decision == DISCARDED:
            actions.append({"aktion": "entfernt", "stem": stem, "datei": f"train/images/{images[stem]}",
                            "grund": "Bildprüfung: verworfen (Skip)"})
            continue
        text = open(os.path.join(review_dir, stem + ".txt"), encoding="utf-8").read()
        lines = [line for line in text.splitlines() if line.strip()]
        if lines:
            actions.append({"aktion": "gelabelt", "stem": stem, "datei": f"train/labels/{stem}.txt", "text": text,
                            "grund": f"Bildprüfung: geprüft, {len(lines)} Rahmen"})
        else:
            actions.append({"aktion": "umbenannt", "stem": stem, "datei": f"train/*/{stem}.*",
                            "neu": f"train/*/{cleanup.MARK_PREFIX}{stem}.*", "text": "",
                            "grund": "Bildprüfung: geprüft, kein Fahrzeug zu sehen: bewusstes Negativ"})
    if problems:
        raise AdoptError("Abbruch, nichts geändert:\n  " + "\n  ".join(problems))
    return actions


def apply(dataset: str, actions: list[dict]) -> None:
    images_dir = os.path.join(dataset, "train", "images")
    labels_dir = os.path.join(dataset, "train", "labels")
    images = check._stems(images_dir, check.IMAGE_EXTENSIONS)
    for item in actions:
        stem = item["stem"]
        if item["aktion"] == "entfernt":
            os.remove(os.path.join(images_dir, images[stem]))
        elif item["aktion"] == "gelabelt":
            with open(os.path.join(labels_dir, stem + ".txt"), "w", encoding="utf-8") as handle:
                handle.write(item["text"])
        else:
            new = cleanup.MARK_PREFIX + stem
            os.rename(os.path.join(images_dir, images[stem]),
                      os.path.join(images_dir, cleanup.MARK_PREFIX + images[stem]))
            with open(os.path.join(labels_dir, new + ".txt"), "w", encoding="utf-8") as handle:
                handle.write("")


def summary(actions: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in actions:
        counts[item["aktion"]] = counts.get(item["aktion"], 0) + 1
    return counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("dataset")
    parser.add_argument("review_dir")
    parser.add_argument("--apply", action="store_true", help="wirklich ändern (sonst nur Probelauf)")
    parser.add_argument("--log", default=cleanup.DEFAULT_LOG)
    args = parser.parse_args(argv)
    try:
        actions = plan(args.dataset, args.review_dir)
    except AdoptError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"{len(actions)} Änderungen: {summary(actions)}" + ("" if args.apply else " (Probelauf, nichts geändert)"))
    if args.apply and actions:
        apply(args.dataset, actions)
        cleanup.append_log(args.log, actions)
        print(f"durchgeführt und protokolliert: {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
