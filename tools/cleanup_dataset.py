"""Einfache Bereinigung des Trainingsdatensatzes mit Änderungsprotokoll (Spec `training-data`).

Zwei Schritte, beide nur für `train`:
  * Labels ohne Bild werden entfernt.
  * Leere Labels ohne Präfix `OFF` (Bild zeigt laut Entscheidung ein bewusstes Negativ) bekommen
    für Bild und Label das Präfix `OFF_` im Namen und gelten danach als bewusste Negative.

Standard ist ein Probelauf (zeigt nur, was passieren würde). Erst mit `--apply` wird geändert und in
das Protokoll geschrieben (`--log`, Standard `data/DATASET_CHANGES.md` im Repo). Vor dem Ändern
sollte eine unveränderte Sicherung des Datensatzes existieren.

    python tools/cleanup_dataset.py <datensatz>            # Probelauf
    python tools/cleanup_dataset.py <datensatz> --apply
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("check_dataset", os.path.join(HERE, "check_dataset.py"))
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

DEFAULT_LOG = os.path.join(os.path.dirname(HERE), "data", "DATASET_CHANGES.md")
MARK_PREFIX = "OFF_"
LOG_HEADER = (
    "# Änderungsprotokoll Trainingsdatensatz\n\n"
    "Jede Änderung am Trainingsset `train` mit Datei, Aktion und Grund. Quelle: `tools/cleanup_dataset.py` und "
    "die Bildprüfung. `valid` und `test` werden nie verändert (Prüfsummen: `HBA4v2.valid_test.sha256`).\n\n"
    "| Datum | Datei | Aktion | Grund |\n|---|---|---|---|\n"
)


def plan(dataset: str) -> list[dict]:
    """Was zu tun ist, ohne etwas zu ändern. Eintrag: {aktion, datei, neu, grund}."""
    images = check._stems(os.path.join(dataset, "train", "images"), check.IMAGE_EXTENSIONS)
    labels = check._stems(os.path.join(dataset, "train", "labels"), (".txt",))
    actions: list[dict] = []
    for stem, label in labels.items():
        path = os.path.join(dataset, "train", "labels", label)
        if stem not in images:
            actions.append({"aktion": "entfernt", "datei": f"train/labels/{label}", "grund": "Label ohne Bild"})
        elif not stem.startswith(check.NEGATIVE_PREFIX) and not open(path, encoding="utf-8", errors="replace").read().strip():
            new = MARK_PREFIX + stem
            actions.append({
                "aktion": "umbenannt", "datei": f"train/*/{stem}.*", "neu": f"train/*/{new}.*", "stem": stem,
                "grund": "leeres Label, Bild zeigt kein Fahrzeug: bewusstes Negativ",
            })
    return actions


def apply(dataset: str, actions: list[dict]) -> None:
    for item in actions:
        if item["aktion"] == "entfernt":
            os.remove(os.path.join(dataset, item["datei"]))
        else:
            stem = item["stem"]
            for folder, extensions in (("images", check.IMAGE_EXTENSIONS), ("labels", (".txt",))):
                found = check._stems(os.path.join(dataset, "train", folder), extensions)[stem]
                os.rename(
                    os.path.join(dataset, "train", folder, found),
                    os.path.join(dataset, "train", folder, MARK_PREFIX + found),
                )


def append_log(log_path: str, actions: list[dict], today: str | None = None) -> None:
    today = today or dt.date.today().isoformat()
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    new_file = not os.path.isfile(log_path)
    with open(log_path, "a", encoding="utf-8") as handle:
        if new_file:
            handle.write(LOG_HEADER)
        for item in actions:
            target = f"{item['datei']} -> {item['neu']}" if "neu" in item else item["datei"]
            handle.write(f"| {today} | `{target}` | {item['aktion']} | {item['grund']} |\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("dataset")
    parser.add_argument("--apply", action="store_true", help="wirklich ändern (sonst nur Probelauf)")
    parser.add_argument("--log", default=DEFAULT_LOG)
    args = parser.parse_args(argv)

    actions = plan(args.dataset)
    for item in actions:
        print(f"{item['aktion']:10} {item['datei']}" + (f"  ->  {item['neu']}" if "neu" in item else ""))
    print(f"{len(actions)} Änderungen" + ("" if args.apply else " (Probelauf, nichts geändert)"))
    if args.apply and actions:
        apply(args.dataset, actions)
        append_log(args.log, actions)
        print(f"durchgeführt und protokolliert: {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
