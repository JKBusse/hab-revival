"""YOLO-Vorlabels in Label-Studio-Aufgaben umwandeln (mit Vorschlägen, die man prüft und korrigiert).

    python tools/yolo_to_ls.py <bildordner> <vorlabelordner> <ausgabe.json> --root <label-studio-dokumentenwurzel>

Für jedes Bild entsteht eine Aufgabe. Liegt zum Bild eine Label-Datei im Vorlabelordner, werden ihre
Rahmen als Vorhersage (`predictions`) mitgegeben. Label Studio zeigt sie als Vorschläge: man
bestätigt oder korrigiert sie. Bildpfade zeigen auf die lokale Dateiablage von Label Studio
(`LOCAL_FILES_SERVING_ENABLED=true`, `LOCAL_FILES_DOCUMENT_ROOT=<root>`).

Koordinaten: YOLO hat Mitte und Größe normiert (0..1), Label Studio linke obere Ecke und Größe in Prozent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

CLASS_NAMES = ["back", "front"]
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
FROM_NAME, TO_NAME = "label", "image"
MODEL_VERSION = "medium6-prelabel"


def yolo_line_to_result(line: str, width: int, height: int) -> dict:
    """Eine YOLO-Zeile als Label-Studio-Ergebnis (Rechteck in Prozent)."""
    cls, xc, yc, w, h = line.split()
    xc, yc, w, h = float(xc), float(yc), float(w), float(h)
    return {
        "from_name": FROM_NAME,
        "to_name": TO_NAME,
        "type": "rectanglelabels",
        "original_width": width,
        "original_height": height,
        "image_rotation": 0,
        "value": {
            "x": round((xc - w / 2) * 100, 6),
            "y": round((yc - h / 2) * 100, 6),
            "width": round(w * 100, 6),
            "height": round(h * 100, 6),
            "rotation": 0,
            "rectanglelabels": [CLASS_NAMES[int(cls)]],
        },
    }


def result_to_yolo_line(result: dict) -> str:
    """Ein Label-Studio-Rechteck als YOLO-Zeile (Mitte und Größe, normiert)."""
    v = result["value"]
    w, h = v["width"] / 100, v["height"] / 100
    xc, yc = v["x"] / 100 + w / 2, v["y"] / 100 + h / 2
    cls = CLASS_NAMES.index(v["rectanglelabels"][0])
    return f"{cls} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"


def build_tasks(image_dir: str, label_dir: str | None, root: str, width: int = 640, height: int = 640) -> list[dict]:
    tasks = []
    for name in sorted(os.listdir(image_dir)):
        stem, ext = os.path.splitext(name)
        if ext.lower() not in IMAGE_EXTENSIONS:
            continue
        relative = os.path.relpath(os.path.join(image_dir, name), root)
        task = {"data": {"image": f"/data/local-files/?d={relative}", "name": name}}
        label_path = os.path.join(label_dir, stem + ".txt") if label_dir else None
        if label_path and os.path.isfile(label_path):
            lines = [l for l in open(label_path, encoding="utf-8").read().splitlines() if l.strip()]
            task["predictions"] = [{
                "model_version": MODEL_VERSION,
                "result": [yolo_line_to_result(line, width, height) for line in lines],
            }]
        tasks.append(task)
    return tasks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("image_dir")
    parser.add_argument("label_dir")
    parser.add_argument("output")
    parser.add_argument("--root", required=True, help="Dokumentenwurzel der lokalen Dateien von Label Studio")
    args = parser.parse_args(argv)
    tasks = build_tasks(args.image_dir, args.label_dir, args.root)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, ensure_ascii=False)
    print(f"{len(tasks)} Aufgaben, davon {sum('predictions' in t for t in tasks)} mit Vorschlägen: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
