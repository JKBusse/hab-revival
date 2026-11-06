"""Kalibrier-Hilfe: Bildausschnitt und Aktive Fläche auf einem Kamerabild einstellen.

    python -m hba.calibrate --image testbild.png [--config hba.yaml]
    python -m hba.calibrate --camera [--config hba.yaml]

Braucht weder GPU noch Modell noch Mikrocontroller und öffnet keinen Serial-Port.

Das Fenster zeigt links das Gesamtbild (nach der Drehung) mit dem Erkennungsausschnitt und rechts
dieses Ausschnitts als 640x640-Eingabebild des Modells mit den Grenzen der Aktiven Fläche, im selben
Maßstab wie der Relevanzfilter.

Maus:   Ausschnitt verschieben oder an den Ecken ziehen (links); gelbe Linie (min_top) und
        Breitenmarke (max_width) ziehen (rechts)
Tasten: s = in die Konfigurationsdatei schreiben, r = zurücksetzen, q = beenden ohne Schreiben

Ohne Display (zum Beispiel auf hba1): `--render-to ausgabe.png` schreibt nur das Bild.
"""

from __future__ import annotations

import argparse
import os
import sys

import cv2
import numpy as np

from hba import exit_codes
from hba.calibration import CalibrationState, MouseController, ViewTransform, bar_y, save
from hba.capture import prepare_frame
from hba.config import MODEL_SIZE, Config, ConfigError, load_config, resolve_config_path

LEFT_WIDTH = 800  # Anzeigebreite des Gesamtbilds
RIGHT_SIZE = 520  # Anzeigegröße der 640x640-Ausschnittsansicht
STATUS_HEIGHT = 56

GREEN = (0, 200, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
HANDLE = 5


def _text(image, text, origin, color=WHITE, scale=0.5):
    cv2.putText(image, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def view_scales(frame_width: int) -> tuple[ViewTransform, ViewTransform]:
    return ViewTransform(LEFT_WIDTH / frame_width), ViewTransform(RIGHT_SIZE / MODEL_SIZE)


def render(state: CalibrationState, frame, base: Config, message: str = "") -> np.ndarray:
    """Das ganze Fenster als Bild. `frame` ist der unrotierte Kameraframe."""
    left_t, right_t = view_scales(state.frame_width)
    shown = cv2.rotate(frame, cv2.ROTATE_180) if base.camera.rotate_180 else frame

    # Links: Gesamtbild mit Ausschnitt und Motorhaubenlinie
    left = cv2.resize(shown, (LEFT_WIDTH, round(shown.shape[0] * left_t.scale)), interpolation=cv2.INTER_AREA)
    x0, y0 = left_t.to_display(state.crop.x0, state.crop.y0)
    x1, y1 = left_t.to_display(state.crop.x1, state.crop.y1)
    cv2.rectangle(left, (x0, y0), (x1, y1), GREEN, 2)
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        cv2.rectangle(left, (cx - HANDLE, cy - HANDLE), (cx + HANDLE, cy + HANDLE), GREEN, -1)
    hood_y = left_t.to_display(0, state.hood_rows)[1]
    cv2.line(left, (0, hood_y), (LEFT_WIDTH, hood_y), RED, 1)
    _text(left, "Motorhaube (ab hier verworfen)", (6, min(hood_y + 16, left.shape[0] - 6)), RED, 0.45)
    _text(left, f"Ausschnitt {state.crop.width}x{state.crop.height}  Zeilen {state.crop.y0}-{state.crop.y1}  "
                f"Spalten {state.crop.x0}-{state.crop.x1}", (6, 18), GREEN)

    # Rechts: Eingabebild des Modells mit Aktiver Fläche, erzeugt mit derselben Funktion wie im Betrieb
    _, model_input = prepare_frame(frame, state.to_config(base))
    right = cv2.resize(model_input, (RIGHT_SIZE, RIGHT_SIZE), interpolation=cv2.INTER_AREA)
    line_y = right_t.to_display(0, state.min_top)[1]
    shade = right.copy()
    cv2.rectangle(shade, (0, 0), (RIGHT_SIZE, line_y), (0, 0, 0), -1)  # nicht relevant: obere Kante zu hoch
    right = cv2.addWeighted(shade, 0.55, right, 0.45, 0)
    cv2.line(right, (0, line_y), (RIGHT_SIZE, line_y), YELLOW, 2)
    _text(right, f"min_top {state.min_top}: obere Kante muss darunter liegen", (6, max(line_y - 6, 14)), YELLOW, 0.45)
    bar_row = right_t.to_display(0, bar_y(state.min_top))[1]
    bar_x = right_t.to_display(state.max_width, 0)[0]
    cv2.line(right, (0, bar_row), (bar_x, bar_row), WHITE, 3)
    cv2.circle(right, (bar_x, bar_row), 7, WHITE, -1)
    _text(right, f"max_width {state.max_width}: Box muss schmaler sein", (6, min(bar_row + 22, RIGHT_SIZE - 6)), WHITE, 0.45)

    height = max(left.shape[0], right.shape[0])
    canvas = np.zeros((height + STATUS_HEIGHT, LEFT_WIDTH + RIGHT_SIZE, 3), dtype=np.uint8)
    canvas[: left.shape[0], :LEFT_WIDTH] = left
    canvas[: right.shape[0], LEFT_WIDTH:] = right
    _text(canvas, "s = speichern   r = zuruecksetzen   q = beenden ohne Schreiben", (8, height + 20), WHITE)
    if message:
        _text(canvas, message[:150], (8, height + 44), YELLOW)
    return canvas


def _load_frame(args, base: Config):
    """Liefert den unrotierten Kameraframe in der konfigurierten Auflösung."""
    if args.image:
        frame = cv2.imread(args.image)
        if frame is None:
            raise ValueError(f"Bild nicht lesbar: {args.image}")
    else:
        from hba.capture import OpenCvCamera

        camera = OpenCvCamera.from_config(base.camera)
        try:
            frame = camera.read()
        finally:
            camera.release()
    size = (base.camera.width, base.camera.height)
    if (frame.shape[1], frame.shape[0]) != size:
        print(f"Hinweis: Bild ist {frame.shape[1]}x{frame.shape[0]}, auf {size[0]}x{size[1]} skaliert", file=sys.stderr)
        frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    return frame


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m hba.calibrate", description=__doc__.split("\n\n")[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--image", help="Testbild (Datei)")
    source.add_argument("--camera", action="store_true", help="ein Bild von der Kamera aufnehmen")
    parser.add_argument("--config", help="Konfigurationsdatei lesen und schreiben (Standard ./hba.yaml)")
    parser.add_argument("--render-to", help="nur ein Bild schreiben, kein Fenster (für Rechner ohne Display)")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = resolve_config_path(args.config)
        target = args.config or path or os.path.join(os.getcwd(), "hba.yaml")
        base = load_config(path, {}).config
        frame = _load_frame(args, base)
    except ConfigError as exc:
        for error in exc.errors:
            print(f"Konfigurationsfehler: {error}", file=sys.stderr)
        return exit_codes.EXIT_CONFIG
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return exit_codes.EXIT_CONFIG

    state = CalibrationState.from_config(base)
    if args.render_to:
        cv2.imwrite(args.render_to, render(state, frame, base))
        return exit_codes.EXIT_OK

    left_t, right_t = view_scales(base.camera.width)
    controller = MouseController(state, left_t, right_t, LEFT_WIDTH)
    message = [f"Datei: {target}"]
    window = "Kalibrierung"

    def on_mouse(event, x, y, flags, _param):
        if event == cv2.EVENT_LBUTTONDOWN:
            controller.on_down(x, y)
        elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
            controller.on_move(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            controller.on_up()

    cv2.namedWindow(window)
    cv2.setMouseCallback(window, on_mouse)
    try:
        while True:
            cv2.imshow(window, render(state, frame, base, message[0]))
            key = cv2.waitKey(30) & 0xFF
            if key == ord("q"):
                return exit_codes.EXIT_OK
            if key == ord("r"):
                fresh = CalibrationState.from_config(base)
                state.crop, state.min_top, state.max_width = fresh.crop, fresh.min_top, fresh.max_width
                message[0] = "zurückgesetzt"
            if key == ord("s"):
                try:
                    save(target, state)
                    message[0] = f"gespeichert: {target}"
                except ConfigError as exc:
                    message[0] = "NICHT gespeichert: " + exc.errors[0]
                    for error in exc.errors:
                        print(f"Konfigurationsfehler: {error}", file=sys.stderr)
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    sys.exit(main())
