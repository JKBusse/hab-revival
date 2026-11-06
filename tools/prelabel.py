"""Vorlabels für Bilder ohne Label mit dem bisherigen Modell erzeugen (läuft auf hba1).

    python tools/prelabel.py <datensatz> <ausgabeordner> [--model best.pt] [--conf 0.25] [-d 0]

Nimmt alle Bilder in `train/images`, zu denen keine Label-Datei existiert, und schreibt für jedes eine
YOLO-Label-Datei in den Ausgabeordner (leer, wenn das Modell nichts sieht). Die Ausgabe liegt bewusst
AUSSERHALB des Trainingssets: Vorlabels sind nur Vorschläge und kommen erst nach der Prüfung durch einen
Menschen ins Set. Die Schwelle ist mit 0,25 niedriger als im Betrieb, damit mehr Treffer als Vorschlag
erscheinen (verpasste Fahrzeuge sind der gefährliche Fehlerfall).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from typing import Callable, Sequence

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("check_dataset", os.path.join(_HERE, "check_dataset.py"))
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

DEFAULT_MODEL = "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt"
DEFAULT_CONF = 0.25

Prediction = tuple  # (klasse, x_mitte, y_mitte, breite, hoehe), normiert 0..1


def unlabeled_images(dataset: str) -> list[str]:
    """Pfade der Bilder in train, zu denen es keine Label-Datei gibt."""
    folder = os.path.join(dataset, "train", "images")
    images = check._stems(folder, check.IMAGE_EXTENSIONS)
    labels = check._stems(os.path.join(dataset, "train", "labels"), (".txt",))
    return [os.path.join(folder, name) for stem, name in images.items() if stem not in labels]


def write_prelabels(
    images: Sequence[str], predict: Callable[[str], Sequence[Prediction]], out_dir: str
) -> dict[str, int]:
    """Schreibt je Bild eine Label-Datei. Liefert {Bildstem: Anzahl Rahmen}."""
    os.makedirs(out_dir, exist_ok=True)
    counts: dict[str, int] = {}
    for path in images:
        stem = os.path.splitext(os.path.basename(path))[0]
        predictions = predict(path)
        with open(os.path.join(out_dir, stem + ".txt"), "w", encoding="utf-8") as handle:
            for cls, xc, yc, w, h in predictions:
                handle.write(f"{int(cls)} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
        counts[stem] = len(predictions)
    return counts


def yolo_predict_fn(model_path: str, conf: float, device: str) -> Callable[[str], Sequence[Prediction]]:
    from ultralytics import YOLO  # erst hier, damit das Modul ohne Torch importierbar bleibt

    model = YOLO(model_path)

    def predict(path: str):
        result = next(iter(model(path, conf=conf, device=device, stream=True, verbose=False)))
        boxes = result.boxes
        out = []
        for cls, xywhn in zip(boxes.cls.tolist(), boxes.xywhn.tolist()):
            out.append((int(cls), *xywhn))
        return out

    return predict


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("dataset")
    parser.add_argument("out_dir")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--conf", type=float, default=DEFAULT_CONF)
    parser.add_argument("-d", "--device", default="0")
    args = parser.parse_args(argv)

    images = unlabeled_images(args.dataset)
    print(f"{len(images)} Bilder ohne Label")
    counts = write_prelabels(images, yolo_predict_fn(args.model, args.conf, args.device), args.out_dir)
    print(f"{len(counts)} Vorlabel-Dateien in {args.out_dir}, davon {sum(1 for c in counts.values() if c)} mit Rahmen, "
          f"{sum(counts.values())} Rahmen insgesamt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
