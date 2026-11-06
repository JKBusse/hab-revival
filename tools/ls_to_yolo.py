"""Geprüfte Label-Studio-Ergebnisse zurück in YOLO-Labels umwandeln.

    python tools/ls_to_yolo.py <export.json> <ausgabeordner>

Jede Aufgabe bekommt eine Entscheidung:
  geprüft       die Aufgabe wurde abgesendet (auch ohne Rahmen: dann steht ein bewusstes Negativ)
  verworfen     die Aufgabe wurde mit Skip übersprungen
  offen         keine Entscheidung (das ist ein Fehler, der Aufruf endet mit Exit-Code 1)

Für `geprüft` entsteht im Ausgabeordner `<stem>.txt`. Zusätzlich schreibt das Skript `entscheidungen.tsv`
(Bildname, Entscheidung). Daraus wird das Änderungsprotokoll gefüllt.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("yolo_to_ls", os.path.join(_HERE, "yolo_to_ls.py"))
_conv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_conv)


def decide(task: dict) -> tuple[str, list[str] | None]:
    """(Entscheidung, YOLO-Zeilen) für eine exportierte Aufgabe. Die letzte nicht übersprungene Annotation zählt."""
    annotations = task.get("annotations") or []
    submitted = [a for a in annotations if not a.get("was_cancelled")]
    if submitted:
        result = submitted[-1].get("result", [])
        return "geprüft", [_conv.result_to_yolo_line(r) for r in result if r.get("type") == "rectanglelabels"]
    if annotations:  # nur Skips
        return "verworfen", None
    return "offen", None


def stem_of(task: dict) -> str:
    name = task["data"].get("name") or os.path.basename(task["data"]["image"].split("d=")[-1])
    return os.path.splitext(name)[0]


def convert(tasks: list[dict], out_dir: str) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    decisions: dict[str, str] = {}
    for task in tasks:
        stem = stem_of(task)
        decision, lines = decide(task)
        decisions[stem] = decision
        if decision == "geprüft":
            with open(os.path.join(out_dir, stem + ".txt"), "w", encoding="utf-8") as handle:
                handle.write("".join(line + "\n" for line in lines))
    with open(os.path.join(out_dir, "entscheidungen.tsv"), "w", encoding="utf-8") as handle:
        for stem in sorted(decisions):
            handle.write(f"{stem}\t{decisions[stem]}\n")
    return decisions


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("export")
    parser.add_argument("out_dir")
    args = parser.parse_args(argv)
    decisions = convert(json.load(open(args.export, encoding="utf-8")), args.out_dir)
    counts = {k: sum(1 for v in decisions.values() if v == k) for k in ("geprüft", "verworfen", "offen")}
    print(f"geprüft {counts['geprüft']}, verworfen {counts['verworfen']}, offen {counts['offen']}")
    for stem, decision in decisions.items():
        if decision == "offen":
            print(f"offen: {stem}")
    return 1 if counts["offen"] else 0


if __name__ == "__main__":
    sys.exit(main())
