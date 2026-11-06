"""Zieht aus Roh-Logs des Fernlicht-Programms kompakte Frame-Auszüge für den Replay-Test.

Eine Zeile pro Frame (JSON, gzip):
    {"t0": Frame-Start, "td": Zeitpunkt der Detektionszeile, "ts": Zeitpunkt der Statuszeile,
     "b": [[x1, y1, x2, y2], ...], "s": geloggter Status}
Zeiten sind Sekunden seit der Epoche (UTC-interpretiert, wie die Log-Zeitstempel).

Das Log enthält weder Klasse noch Konfidenz der Boxen. Der Replay nimmt Konfidenz über der
Schwelle an (das Modell filtert bereits mit derselben Schwelle).

Ein Frame beginnt bei `-Frame START-` und gilt als vollständig, sobald `HBA Status` folgt.
Ist `-S` oder `-v` aktiv, stehen die `cord0:`-Zeilen doppelt (gerundet). Es zählen nur die
ersten N Boxen hinter `Detections: N`.

Aufruf:  python extract_replay.py <ausgabeordner> <log> [<log> ...]
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import re
import sys

TS = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),(\d{3})")
CORDS = re.compile(r"cord0: ([\d.]+) cord1: ([\d.]+) cord2: ([\d.]+) cord3: ([\d.]+)")
DETECTIONS = re.compile(r"Detections: (\d+)")
STATUS = re.compile(r"HBA Status: (\d)")


def epoch(line):
    m = TS.match(line)
    if not m:
        return None
    moment = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
    return round(int(moment.timestamp()) + int(m.group(2)) / 1000.0, 3)


def frames_from_log(path):
    frames, cur = [], None
    expected = 0
    for line in open(path, errors="ignore"):
        if "-Frame START-" in line:
            if cur is not None and cur["s"] is not None:
                frames.append(cur)
            cur = {"t0": epoch(line), "td": None, "ts": None, "b": [], "s": None}
            expected = 0
            continue
        if cur is None:
            continue
        m = DETECTIONS.search(line)
        if m and cur["td"] is None:
            cur["td"] = epoch(line)
            expected = int(m.group(1))
            continue
        m = CORDS.search(line)
        if m and len(cur["b"]) < expected:
            cur["b"].append([float(x) for x in m.groups()])
            continue
        m = STATUS.search(line)
        if m and cur["s"] is None:
            cur["ts"] = epoch(line)
            cur["s"] = int(m.group(1))
    if cur is not None and cur["s"] is not None:
        frames.append(cur)
    return frames


def main(argv):
    out_dir, logs = argv[1], argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    for path in logs:
        frames = frames_from_log(path)
        name = os.path.splitext(os.path.basename(path))[0] + ".jsonl.gz"
        target = os.path.join(out_dir, name)
        with gzip.GzipFile(target, "wb", mtime=0) as handle:  # mtime=0: reproduzierbare Bytes
            for frame in frames:
                handle.write((json.dumps(frame, separators=(",", ":")) + "\n").encode())
        transitions = sum(1 for a, b in zip(frames, frames[1:]) if a["s"] != b["s"])
        with_boxes = sum(1 for f in frames if f["b"])
        digest = hashlib.sha256(open(target, "rb").read()).hexdigest()[:16]
        print(f"{os.path.basename(path)}: frames={len(frames)} statuswechsel={transitions} "
              f"frames_mit_boxen={with_boxes} -> {name} ({os.path.getsize(target)} Byte, sha256 {digest})")


if __name__ == "__main__":
    main(sys.argv)
