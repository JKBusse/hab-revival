"""Konfiguration: Standardwerte, Laden aus YAML, Vorrang und Prüfung beim Start.

Vorrang: Kommandozeilen-Flag, dann Konfigurationsdatei, dann eingebauter Standard.
Die eingebauten Standardwerte entsprechen dem bisherigen Verhalten des Legacy-Skripts
(`legacy/yolov8.py`). Ein Start ohne Datei verhält sich daher wie vorher.

Fehler werden gesammelt und gemeinsam als `ConfigError` gemeldet. Das Programm beendet sich dann
mit Exit-Code 2. Eine Haltezeit unter 3 s ist nur eine Warnung (Entscheidung von Jan).
"""

from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from typing import Any, Callable

MODEL_SIZE = 640  # Eingabegröße des Modells, fest

# Eingebaute Standardwerte (= bisheriges Verhalten)
DEFAULTS: dict[str, dict[str, Any]] = {
    "camera": {
        "device": 0,
        "width": 1920,
        "height": 1080,
        "rotate_180": True,
        "exposure": 1,
        "exposure_time": 700,
        "brightness": None,
    },
    "image": {
        "hood_rows": 850,
        "crop_rows": [212, 638],
        "crop_cols": [400, 1360],
    },
    "detection": {
        "model": "/home/jkb/HBA4v2Dataset/HBAv5/medium6/weights/best.pt",
        "device": "0",
        "conf": 0.4,
    },
    "relevance": {"max_width": 500, "min_top": 160},
    "decision": {"hold_seconds": 3},
    "serial": {"port": "/dev/ttyUSB0", "baudrate": 9600},
    "recording": {
        "path": "/mnt/hba-stick/HBA/",
        "sample_probability": 1 / 99,  # Legacy: randrange(1, 100) == 42
        "detection_probability": 9 / 99,  # Legacy: randrange(1, 100) > 90
        "max_files": 1000,
    },
    "output": {"video": False, "stream": False, "save": False},
}

# Kommandozeilen-Flag -> Schlüssel
FLAG_KEYS = {
    "conf": ("detection", "conf"),
    "device": ("detection", "device"),
    "model": ("detection", "model"),
    "exposure": ("camera", "exposure"),
    "time": ("camera", "exposure_time"),
    "brightness": ("camera", "brightness"),
    "path": ("recording", "path"),
    "video": ("output", "video"),
    "stream": ("output", "stream"),
    "save": ("output", "save"),
}

DEFAULT_FILE = "hba.yaml"
RECOMMENDED_HOLD_SECONDS = 3


class ConfigError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


# --- Typen --------------------------------------------------------------------------------

@dataclass(frozen=True)
class CameraConfig:
    device: int
    width: int
    height: int
    rotate_180: bool
    exposure: int
    exposure_time: int
    brightness: int | None


@dataclass(frozen=True)
class ImageConfig:
    hood_rows: int
    crop_rows: tuple[int, int]
    crop_cols: tuple[int, int]


@dataclass(frozen=True)
class DetectionConfig:
    model: str
    device: str
    conf: float


@dataclass(frozen=True)
class RelevanceConfig:
    max_width: float
    min_top: float


@dataclass(frozen=True)
class DecisionConfig:
    hold_seconds: float


@dataclass(frozen=True)
class SerialConfig:
    port: str
    baudrate: int


@dataclass(frozen=True)
class RecordingConfig:
    path: str
    sample_probability: float
    detection_probability: float
    max_files: int


@dataclass(frozen=True)
class OutputConfig:
    video: bool
    stream: bool
    save: bool


@dataclass(frozen=True)
class Config:
    camera: CameraConfig
    image: ImageConfig
    detection: DetectionConfig
    relevance: RelevanceConfig
    decision: DecisionConfig
    serial: SerialConfig
    recording: RecordingConfig
    output: OutputConfig

    @classmethod
    def defaults(cls) -> "Config":
        return _build(copy.deepcopy(DEFAULTS))


@dataclass(frozen=True)
class LoadedConfig:
    config: Config
    sources: dict[str, str]  # "camera.device" -> "Standard" | "Datei" | "Flag"
    warnings: list[str]
    path: str | None


# --- Prüfer für einzelne Werte ---------------------------------------------------------------

def _int(minimum=None, maximum=None, allow_none=False) -> Callable[[Any], Any]:
    def check(value):
        if value is None and allow_none:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("muss eine ganze Zahl sein")
        if minimum is not None and value < minimum:
            raise ValueError(f"muss mindestens {minimum} sein")
        if maximum is not None and value > maximum:
            raise ValueError(f"darf höchstens {maximum} sein")
        return value

    return check


def _number(minimum=None, maximum=None, exclusive_min=False) -> Callable[[Any], float]:
    def check(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("muss eine Zahl sein")
        if minimum is not None and (value <= minimum if exclusive_min else value < minimum):
            raise ValueError(f"muss {'größer als' if exclusive_min else 'mindestens'} {minimum} sein")
        if maximum is not None and value > maximum:
            raise ValueError(f"darf höchstens {maximum} sein")
        return float(value)

    return check


def _bool(value):
    if not isinstance(value, bool):
        raise ValueError("muss wahr oder falsch sein (true/false)")
    return value


def _str(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("muss ein nicht leerer Text sein")
    return value


def _pair(value):
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or any(isinstance(v, bool) or not isinstance(v, int) for v in value)
    ):
        raise ValueError("muss eine Liste aus zwei ganzen Zahlen sein, zum Beispiel [212, 638]")
    return [int(value[0]), int(value[1])]


def _device(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError('muss "cpu" oder ein GPU-Index sein, zum Beispiel "0"')
    return str(value)


def _exposure(value):
    if isinstance(value, bool) or value not in (1, 3):
        raise ValueError("muss 1 (manuell) oder 3 (automatisch) sein")
    return value


CHECKS: dict[str, Callable[[Any], Any]] = {
    "camera.device": _int(0),
    "camera.width": _int(1),
    "camera.height": _int(1),
    "camera.rotate_180": _bool,
    "camera.exposure": _exposure,
    "camera.exposure_time": _int(0, 5000),
    "camera.brightness": _int(-180, 180, allow_none=True),
    "image.hood_rows": _int(1),
    "image.crop_rows": _pair,
    "image.crop_cols": _pair,
    "detection.model": _str,
    "detection.device": _device,
    "detection.conf": _number(0, 1),
    "relevance.max_width": _number(0, exclusive_min=True),
    "relevance.min_top": _number(0),
    "decision.hold_seconds": _number(0, exclusive_min=True),
    "serial.port": _str,
    "serial.baudrate": _int(1),
    "recording.path": _str,
    "recording.sample_probability": _number(0, 1),
    "recording.detection_probability": _number(0, 1),
    "recording.max_files": _int(1),
    "output.video": _bool,
    "output.stream": _bool,
    "output.save": _bool,
}


# --- Laden --------------------------------------------------------------------------------------

def resolve_config_path(explicit: str | None, cwd: str | None = None) -> str | None:
    """`--config <pfad>`, sonst `./hba.yaml`, sonst keine Datei (nur Standardwerte)."""
    if explicit is not None:
        if not os.path.isfile(explicit):
            raise ConfigError([f"Konfigurationsdatei nicht gefunden: {explicit}"])
        return explicit
    candidate = os.path.join(cwd if cwd is not None else os.getcwd(), DEFAULT_FILE)
    return candidate if os.path.isfile(candidate) else None


def _read_yaml(path: str) -> dict:
    from ruamel.yaml import YAML
    from ruamel.yaml.error import YAMLError

    try:
        with open(path, encoding="utf-8") as handle:
            data = YAML(typ="safe").load(handle)
    except (OSError, YAMLError) as exc:
        raise ConfigError([f"Konfigurationsdatei nicht lesbar ({path}): {exc}"]) from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError([f"Konfigurationsdatei muss Abschnitte enthalten (camera:, image:, ...): {path}"])
    return data


def _flag_values(flags: dict[str, Any], errors: list[str]) -> dict[tuple[str, str], Any]:
    """Wandelt die gegebenen Flags in Werte um. Nicht gegebene Flags (None) fehlen."""
    out: dict[tuple[str, str], Any] = {}
    for flag, value in flags.items():
        if value is None or flag not in FLAG_KEYS:
            continue
        key = FLAG_KEYS[flag]
        if flag in ("exposure", "time", "brightness"):  # kommen als Text von der Kommandozeile
            try:
                value = int(value)
            except (TypeError, ValueError):
                errors.append(f"Flag --{flag}: muss eine ganze Zahl sein, war {value!r}")
                continue
        out[key] = value
    return out


def load_config(path: str | None, flags: dict[str, Any] | None = None) -> LoadedConfig:
    errors: list[str] = []
    merged = copy.deepcopy(DEFAULTS)
    sources = {f"{section}.{key}": "Standard" for section, keys in DEFAULTS.items() for key in keys}

    if path is not None:
        data = _read_yaml(path)
        for section, content in data.items():
            if section not in DEFAULTS:
                errors.append(f"Unbekannter Abschnitt: {section}")
            elif not isinstance(content, dict):
                errors.append(f"Abschnitt {section} muss Einträge enthalten")
            else:
                for key, value in content.items():
                    if key not in DEFAULTS[section]:
                        errors.append(f"Unbekannter Schlüssel: {section}.{key}")
                    else:
                        merged[section][key] = value
                        sources[f"{section}.{key}"] = "Datei"

    for (section, key), value in _flag_values(flags or {}, errors).items():
        merged[section][key] = value
        sources[f"{section}.{key}"] = "Flag"

    failed: set[str] = set()
    for dotted, check in CHECKS.items():
        section, key = dotted.split(".")
        try:
            merged[section][key] = check(merged[section][key])
        except ValueError as exc:
            failed.add(dotted)
            errors.append(f"{dotted}: {exc} (war {merged[section][key]!r}, Quelle: {sources[dotted]})")

    errors += _cross_checks(merged, failed)
    if errors:
        raise ConfigError(errors)

    warnings = []
    hold = merged["decision"]["hold_seconds"]
    if hold < RECOMMENDED_HOLD_SECONDS:
        warnings.append(
            f"Haltezeit {hold:g} s ist kürzer als die bewährten {RECOMMENDED_HOLD_SECONDS} s: "
            "das Fernlicht wird früher wieder freigegeben"
        )
    return LoadedConfig(_build(merged), sources, warnings, path)


def _cross_checks(merged: dict, failed: set[str]) -> list[str]:
    """Querbeziehungen. Jede Prüfung läuft nur, wenn die beteiligten Einzelwerte gültig sind."""

    def usable(*keys: str) -> bool:
        return not failed.intersection(keys)

    errors = []
    cam, img, rel = merged["camera"], merged["image"], merged["relevance"]
    if usable("image.hood_rows", "camera.height") and img["hood_rows"] > cam["height"]:
        errors.append(f"image.hood_rows ({img['hood_rows']}) ragt über die Bildhöhe ({cam['height']}) hinaus")
    if usable("image.crop_rows", "image.hood_rows", "camera.height"):
        r0, r1 = img["crop_rows"]
        limit = min(img["hood_rows"], cam["height"])
        if not 0 <= r0 < r1:
            errors.append(f"image.crop_rows {img['crop_rows']}: Anfang muss kleiner als Ende sein und nicht negativ")
        elif r1 > limit:
            errors.append(f"image.crop_rows {img['crop_rows']} ragt über das Bild hinaus (erlaubt bis Zeile {limit})")
    if usable("image.crop_cols", "camera.width"):
        c0, c1 = img["crop_cols"]
        if not 0 <= c0 < c1:
            errors.append(f"image.crop_cols {img['crop_cols']}: Anfang muss kleiner als Ende sein und nicht negativ")
        elif c1 > cam["width"]:
            errors.append(f"image.crop_cols {img['crop_cols']} ragt über die Bildbreite ({cam['width']}) hinaus")
    if usable("relevance.min_top") and rel["min_top"] >= MODEL_SIZE:
        errors.append(f"relevance.min_top ({rel['min_top']:g}) muss kleiner als {MODEL_SIZE} sein")
    return errors


def _build(merged: dict) -> Config:
    img = merged["image"]
    return Config(
        camera=CameraConfig(**merged["camera"]),
        image=ImageConfig(
            hood_rows=img["hood_rows"],
            crop_rows=tuple(img["crop_rows"]),
            crop_cols=tuple(img["crop_cols"]),
        ),
        detection=DetectionConfig(**merged["detection"]),
        relevance=RelevanceConfig(**merged["relevance"]),
        decision=DecisionConfig(**merged["decision"]),
        serial=SerialConfig(**merged["serial"]),
        recording=RecordingConfig(**merged["recording"]),
        output=OutputConfig(**merged["output"]),
    )


def describe(loaded: LoadedConfig) -> list[str]:
    """Logzeilen mit allen effektiven Werten und ihrer Quelle."""
    lines = []
    for section in DEFAULTS:
        values = getattr(loaded.config, section)
        for key in DEFAULTS[section]:
            lines.append(f"config {section}.{key} = {getattr(values, key)!r} ({loaded.sources[f'{section}.{key}']})")
    return lines
