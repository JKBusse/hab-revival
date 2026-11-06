"""Prüfroutine für den Trainingsdatensatz (Spec `training-data`).

Regeln (je Verstoß eine Zeile mit Dateiname):
  * Jedes Bild hat eine Label-Datei. Leer ist ein Label nur bei bewussten Negativen (Namenspräfix `OFF`).
  * Keine Label-Dateien ohne Bild.
  * Nur die Klassen `back` (0) und `front` (1), kleingeschrieben, in `data.yaml` in dieser Reihenfolge.
  * Jede Label-Zeile hat die Form `<klasse> <x> <y> <b> <h>` mit vier Zahlen zwischen 0 und 1.

Aufruf:
    python tools/check_dataset.py <datensatz> [--splits train,valid,test]
    python tools/check_dataset.py <datensatz> --write-checksums valid_test.sha256
    python tools/check_dataset.py <datensatz> --verify-checksums valid_test.sha256

Ohne Option prüft es nur `train` (nur dort gelten die Regeln der Spec). Exit-Code 0 ohne Verstöße,
sonst 1. Das Training ruft die Routine auf und startet bei Verstößen nicht.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
NEGATIVE_PREFIX = "OFF"
CLASS_NAMES = ["back", "front"]
FROZEN_SPLITS = ("valid", "test")


def _stems(folder: str, extensions: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    if not os.path.isdir(folder):
        return out
    for name in sorted(os.listdir(folder)):
        stem, ext = os.path.splitext(name)
        if ext.lower() in extensions:
            out[stem] = name
    return out


def check_label_file(path: str, name: str, is_negative: bool) -> list[str]:
    violations: list[str] = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if not lines:
        if not is_negative:
            violations.append(f"{name}: leeres Label ohne Präfix {NEGATIVE_PREFIX} (kein bewusstes Negativ)")
        return violations
    for number, line in enumerate(lines, 1):
        parts = line.split()
        where = f"{name}, Zeile {number}"
        if len(parts) != 5:
            violations.append(f"{where}: erwartet 5 Werte, gefunden {len(parts)}")
            continue
        try:
            cls = int(parts[0])
        except ValueError:
            violations.append(f"{where}: Klasse ist keine ganze Zahl ({parts[0]!r})")
            continue
        if cls not in range(len(CLASS_NAMES)):
            violations.append(f"{where}: unbekannter Klassenindex {cls}")
        for value in parts[1:]:
            try:
                number_value = float(value)
            except ValueError:
                violations.append(f"{where}: kein Zahlenwert ({value!r})")
                break
            if not 0.0 <= number_value <= 1.0:
                violations.append(f"{where}: Wert {number_value} außerhalb 0 bis 1")
                break
    return violations


def check_data_yaml(dataset: str) -> list[str]:
    path = os.path.join(dataset, "data.yaml")
    if not os.path.isfile(path):
        return ["data.yaml: fehlt"]
    from ruamel.yaml import YAML

    data = YAML(typ="safe").load(open(path, encoding="utf-8"))
    names = data.get("names") if isinstance(data, dict) else None
    if names != CLASS_NAMES:
        return [f"data.yaml: names ist {names!r}, erwartet {CLASS_NAMES!r} (kleingeschrieben, diese Reihenfolge)"]
    return []


def check_split(dataset: str, split: str) -> list[str]:
    violations: list[str] = []
    images = _stems(os.path.join(dataset, split, "images"), IMAGE_EXTENSIONS)
    labels = _stems(os.path.join(dataset, split, "labels"), (".txt",))
    if not images and not labels:
        return [f"{split}: keine Bilder und keine Labels gefunden"]
    for stem, image in images.items():
        if stem not in labels:
            violations.append(f"{split}/images/{image}: keine Label-Datei")
    for stem, label in labels.items():
        if stem not in images:
            violations.append(f"{split}/labels/{label}: Label ohne Bild")
        else:
            violations += check_label_file(
                os.path.join(dataset, split, "labels", label),
                f"{split}/labels/{label}",
                is_negative=stem.startswith(NEGATIVE_PREFIX),
            )
    return violations


def check_dataset(dataset: str, splits: tuple[str, ...] = ("train",)) -> list[str]:
    violations = check_data_yaml(dataset)
    for split in splits:
        violations += check_split(dataset, split)
    return violations


def checksums(dataset: str, splits: tuple[str, ...] = FROZEN_SPLITS) -> dict[str, str]:
    """SHA-256 jeder Datei der angegebenen Splits (Pfad relativ zum Datensatz)."""
    out: dict[str, str] = {}
    for split in splits:
        for dirpath, _, files in os.walk(os.path.join(dataset, split)):
            for name in files:
                if name.startswith("."):  # zum Beispiel .DS_Store: vom Finder verändert, kein Datensatzinhalt
                    continue
                path = os.path.join(dirpath, name)
                digest = hashlib.sha256()
                with open(path, "rb") as handle:
                    for chunk in iter(lambda: handle.read(1 << 20), b""):
                        digest.update(chunk)
                out[os.path.relpath(path, dataset)] = digest.hexdigest()
    return out


def write_checksums(dataset: str, target: str) -> int:
    data = checksums(dataset)
    with open(target, "w", encoding="utf-8") as handle:
        for key in sorted(data):
            handle.write(f"{data[key]}  {key}\n")
    return len(data)


def verify_checksums(dataset: str, source: str) -> list[str]:
    expected: dict[str, str] = {}
    for line in open(source, encoding="utf-8"):
        digest, _, key = line.rstrip("\n").partition("  ")
        if key:
            expected[key] = digest
    actual = checksums(dataset)
    problems = [f"{key}: fehlt" for key in sorted(expected.keys() - actual.keys())]
    problems += [f"{key}: neu hinzugekommen" for key in sorted(actual.keys() - expected.keys())]
    problems += [f"{key}: Inhalt verändert" for key in sorted(expected.keys() & actual.keys()) if expected[key] != actual[key]]
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("dataset")
    parser.add_argument("--splits", default="train", help="kommagetrennt, Standard: train")
    parser.add_argument("--write-checksums", metavar="DATEI", help="Prüfsummen von valid und test schreiben")
    parser.add_argument("--verify-checksums", metavar="DATEI", help="valid und test gegen die Prüfsummen prüfen")
    args = parser.parse_args(argv)

    if args.write_checksums:
        print(f"{write_checksums(args.dataset, args.write_checksums)} Prüfsummen geschrieben: {args.write_checksums}")
        return 0
    if args.verify_checksums:
        problems = verify_checksums(args.dataset, args.verify_checksums)
        for problem in problems:
            print(problem)
        print("valid und test unverändert" if not problems else f"{len(problems)} Abweichungen")
        return 1 if problems else 0

    violations = check_dataset(args.dataset, tuple(s for s in args.splits.split(",") if s))
    for violation in violations:
        print(violation)
    print(f"{len(violations)} Verstöße" if violations else "keine Verstöße")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
