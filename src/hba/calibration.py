"""Kalibrier-Hilfe: Logik ohne Fenster (Geometrie, Maussteuerung, Prüfen, Schreiben).

Das Fenster selbst steht in `hba.calibrate`. Hier liegt alles, was sich ohne Display testen lässt.

Koordinaten:
* Gesamtbild: der Kameraframe nach der Drehung, wie ihn `prepare_frame` zuschneidet. Der Erkennungsausschnitt
  (`image.crop_rows`, `image.crop_cols`) ist ein Rechteck darin.
* Ausschnittsansicht: das 640x640-Eingabebild des Modells. Darin liegen die Grenzen der Aktiven Fläche
  (`relevance.min_top`, `relevance.max_width`), im selben Maßstab wie der Relevanzfilter.
"""

from __future__ import annotations

import copy
import dataclasses
import os
import tempfile
from dataclasses import dataclass
from typing import Any

from hba.config import MODEL_SIZE, Config, ConfigError, LoadedConfig, load_config_data

HANDLE_TOLERANCE = 12  # Pixel in der Anzeige
MIN_RECT = 20  # kleinster Ausschnitt in Bildpixeln


# --- Rechteck ---------------------------------------------------------------------------------

@dataclass(frozen=True)
class Rect:
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0


def rect_from_image_config(crop_rows, crop_cols) -> Rect:
    return Rect(x0=crop_cols[0], y0=crop_rows[0], x1=crop_cols[1], y1=crop_rows[1])


def move_rect(rect: Rect, dx: int, dy: int, max_x: int, max_y: int) -> Rect:
    """Verschiebt das Rechteck, ohne seine Größe zu ändern. Es bleibt im Bereich 0..max."""
    dx = max(-rect.x0, min(dx, max_x - rect.x1))
    dy = max(-rect.y0, min(dy, max_y - rect.y1))
    return Rect(rect.x0 + dx, rect.y0 + dy, rect.x1 + dx, rect.y1 + dy)


def resize_rect(rect: Rect, handle: str, x: int, y: int, max_x: int, max_y: int, minimum: int = MIN_RECT) -> Rect:
    """Zieht eine Ecke (`tl`, `tr`, `bl`, `br`) auf den Punkt (x, y). Das Rechteck bleibt im Bereich."""
    x = max(0, min(x, max_x))
    y = max(0, min(y, max_y))
    x0, y0, x1, y1 = rect.x0, rect.y0, rect.x1, rect.y1
    if handle in ("tl", "bl"):
        x0 = min(x, x1 - minimum)
    else:
        x1 = max(x, x0 + minimum)
    if handle in ("tl", "tr"):
        y0 = min(y, y1 - minimum)
    else:
        y1 = max(y, y0 + minimum)
    return Rect(max(0, x0), max(0, y0), min(max_x, x1), min(max_y, y1))


def hit_handle(rect: Rect, x: float, y: float, tolerance: float) -> str | None:
    """`tl`/`tr`/`bl`/`br` nahe einer Ecke, `move` im Inneren, sonst None. (Alles in denselben Einheiten.)"""
    corners = {"tl": (rect.x0, rect.y0), "tr": (rect.x1, rect.y0), "bl": (rect.x0, rect.y1), "br": (rect.x1, rect.y1)}
    for name, (cx, cy) in corners.items():
        if abs(x - cx) <= tolerance and abs(y - cy) <= tolerance:
            return name
    if rect.x0 <= x <= rect.x1 and rect.y0 <= y <= rect.y1:
        return "move"
    return None


def bar_y(min_top: int) -> int:
    """Höhe der Breitenmarke in der Ausschnittsansicht (knapp unter der Linie)."""
    return min(MODEL_SIZE - 20, min_top + 30)


# --- Anzeige <-> Bild -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ViewTransform:
    """Maßstab einer Ansicht: Anzeige = Bild * scale."""

    scale: float

    def to_image(self, x: float, y: float) -> tuple[int, int]:
        return round(x / self.scale), round(y / self.scale)

    def to_display(self, x: float, y: float) -> tuple[int, int]:
        return round(x * self.scale), round(y * self.scale)


# --- Zustand und Maussteuerung --------------------------------------------------------------------

@dataclass
class CalibrationState:
    crop: Rect
    min_top: int
    max_width: int
    hood_rows: int
    frame_width: int
    frame_height: int

    @classmethod
    def from_config(cls, config: Config) -> "CalibrationState":
        return cls(
            crop=rect_from_image_config(config.image.crop_rows, config.image.crop_cols),
            min_top=round(config.relevance.min_top),
            max_width=round(config.relevance.max_width),
            hood_rows=config.image.hood_rows,
            frame_width=config.camera.width,
            frame_height=config.camera.height,
        )

    @property
    def max_row(self) -> int:
        return min(self.hood_rows, self.frame_height)

    def to_config(self, base: Config) -> Config:
        """Eine Konfiguration mit den hier eingestellten Werten (für Anzeige und Prüfung)."""
        return dataclasses.replace(
            base,
            image=dataclasses.replace(
                base.image,
                crop_rows=(self.crop.y0, self.crop.y1),
                crop_cols=(self.crop.x0, self.crop.x1),
            ),
            relevance=dataclasses.replace(base.relevance, min_top=self.min_top, max_width=self.max_width),
        )

    def overrides(self) -> dict[str, dict[str, Any]]:
        return {
            "image": {"crop_rows": [self.crop.y0, self.crop.y1], "crop_cols": [self.crop.x0, self.crop.x1]},
            "relevance": {"min_top": self.min_top, "max_width": self.max_width},
        }


class MouseController:
    """Setzt Mausbewegungen in Änderungen am Zustand um.

    Das Fenster besteht aus zwei Ansichten nebeneinander: links das Gesamtbild (Breite `left_width`
    in Anzeigepixeln, Maßstab `left`), rechts die 640x640-Ausschnittsansicht (Maßstab `right`).
    """

    def __init__(self, state: CalibrationState, left: ViewTransform, right: ViewTransform, left_width: int):
        self.state = state
        self.left = left
        self.right = right
        self.left_width = left_width
        self._drag: tuple | None = None

    def on_down(self, x: int, y: int) -> None:
        s = self.state
        if x < self.left_width:
            ix, iy = self.left.to_image(x, y)
            tol = HANDLE_TOLERANCE / self.left.scale
            handle = hit_handle(s.crop, ix, iy, tol)
            if handle == "move":
                self._drag = ("move", ix, iy, s.crop)
            elif handle is not None:
                self._drag = ("resize", handle)
            return
        vx, vy = self.right.to_image(x - self.left_width, y)
        tol = HANDLE_TOLERANCE / self.right.scale
        if abs(vy - s.min_top) <= tol:
            self._drag = ("min_top",)
        elif abs(vy - self.bar_y) <= tol and abs(vx - s.max_width) <= tol:
            self._drag = ("max_width",)

    @property
    def bar_y(self) -> int:
        return bar_y(self.state.min_top)

    def on_move(self, x: int, y: int) -> None:
        if self._drag is None:
            return
        s = self.state
        kind = self._drag[0]
        if kind == "move":
            _, sx, sy, start = self._drag
            ix, iy = self.left.to_image(x, y)
            s.crop = move_rect(start, ix - sx, iy - sy, s.frame_width, s.max_row)
        elif kind == "resize":
            ix, iy = self.left.to_image(x, y)
            s.crop = resize_rect(s.crop, self._drag[1], ix, iy, s.frame_width, s.max_row)
        elif kind == "min_top":
            _, vy = self.right.to_image(x - self.left_width, y)
            s.min_top = max(0, min(vy, MODEL_SIZE - 1))
        elif kind == "max_width":
            vx, _ = self.right.to_image(x - self.left_width, y)
            s.max_width = max(1, min(vx, MODEL_SIZE))

    def on_up(self) -> None:
        self._drag = None


# --- Prüfen und Schreiben --------------------------------------------------------------------------------

def read_file_data(path: str | None) -> dict:
    if path is None or not os.path.isfile(path):
        return {}
    from hba.config import _read_yaml

    return _read_yaml(path)


def validate_overrides(path: str | None, overrides: dict[str, dict[str, Any]]) -> LoadedConfig:
    """Prüft die Datei mit den neuen Werten wie beim Programmstart. Wirft `ConfigError`."""
    data = copy.deepcopy(read_file_data(path))
    for section, values in overrides.items():
        data.setdefault(section, {}).update(values)
    return load_config_data(data, None, path)


def write_overrides(path: str, overrides: dict[str, dict[str, Any]]) -> None:
    """Schreibt nur die geänderten Schlüssel in die YAML-Datei. Kommentare und übrige Schlüssel
    bleiben erhalten. Die Datei wird atomar ersetzt (temporäre Datei im selben Ordner, `os.replace`)."""
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap, CommentedSeq

    yaml = YAML(typ="rt")
    # `null` bleibt `null` (ruamel würde es sonst als leeren Wert schreiben und die Zeile ändern).
    yaml.representer.add_representer(
        type(None), lambda representer, data: representer.represent_scalar("tag:yaml.org,2002:null", "null")
    )
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)

    exists = os.path.isfile(path)
    data = yaml.load(open(path, encoding="utf-8")) if exists else None
    if data is None:
        data = CommentedMap()

    for section, values in overrides.items():
        target = data.get(section)
        if target is None:
            target = CommentedMap()
            data[section] = target
        for key, value in values.items():
            current = target.get(key)
            if isinstance(value, list) and isinstance(current, list) and len(current) == len(value):
                for i, item in enumerate(value):  # in place: Stil und Kommentare bleiben
                    current[i] = item
            elif isinstance(value, list):
                seq = CommentedSeq(value)
                seq.fa.set_flow_style()
                target[key] = seq
            else:
                target[key] = value

    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".hba-", suffix=".yaml.tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            yaml.dump(data, handle)
        if exists:
            os.chmod(tmp, os.stat(path).st_mode & 0o777)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def save(path: str, state: CalibrationState) -> LoadedConfig:
    """Prüft und schreibt. Bei ungültigen Werten wird nichts geschrieben (`ConfigError`)."""
    overrides = state.overrides()
    loaded = validate_overrides(path, overrides)
    write_overrides(path, overrides)
    return loaded
