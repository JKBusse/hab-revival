# Design

## Context

Motivation und Umfang stehen in `proposal.md`. Dieser Change ändert kein beobachtbares Verhalten, deshalb gibt es keine Delta-Specs. Als Referenz gelten die acht Baseline-Specs in `openspec/specs/`.

Ausgangslage: `legacy/yolov8.py` ist ein Skript mit Endlosloop auf Modulebene und globalem Zustand. Gemessen auf `hba1` (GPU): Frame-Dauer Median 0,08 bis 0,12 s, Maximum 0,16 s. Die Umgebungen unterscheiden sich:

| | Mac (Entwicklung) | `hba1` (Betrieb) |
|---|---|---|
| Python | 3.13, Intel x86_64 | 3.10.12 |
| torch / ultralytics | nicht installiert | 2.0.1+cu117 / 8.0.180 (Pins) |
| Kamera, Serial, GPU | keine | vorhanden |

## Goals / Non-Goals

**Goals:**
- Jedes Modul ist ohne Kamera, GPU und Mikrocontroller testbar.
- Verhalten und Log-Meldungen entsprechen dem Legacy-System.
- Der Code läuft unter Python 3.10 und 3.13.

**Non-Goals:**
- Keine Verhaltensänderung und keine Fehlerbehebung (siehe die Folge-Changes).
- Keine Konfigurationsdatei, kein Dienst, kein Upgrade von torch oder ultralytics.

## Decisions

### 1. Ports und Adapter, vier Schnittstellen

Nur das, was Hardware oder Zeit berührt, liegt hinter einer Schnittstelle: `Camera`, `Detector`, `Actuator` und `Clock`. Relevanzfilter, Entscheidung, Datensammlung und Monitoring sind reine Logik. Zusammengesetzt wird in `app.py`.

*Alternative:* Eine Klasse für die gesamte Pipeline. Verworfen, weil dann wieder nichts einzeln prüfbar wäre.

### 2. Der Detektor lädt ultralytics erst beim Start

`detect.py` importiert `ultralytics` und `torch` nur in der Adapter-Klasse, nicht auf Modulebene. Auf dem Mac läuft die gesamte Testsuite deshalb ohne Torch gegen einen Fake-Detektor. Die Pins auf `hba1` bleiben unverändert.

### 3. Die Entscheidung ist eine reine Funktion

`decide(state, relevant_boxes, now_seconds) -> (state, status)` hält den Zustand (`lastDetectTimer`, `lastDetectTimer1`) explizit und bekommt die Zeit als ganze Sekunden übergeben, so wie das Original mit `int(time.time())` rechnet. Das ist die Voraussetzung für den Replay mit echten Logs in `multi-box-decision`.

### 4. Zufall und Zeit sind einspeisbar

Der Recorder bekommt ein `random.Random`, die Pipeline eine `Clock`. Tests setzen feste Seeds und eine Fake-Uhr.

### 5. Legacy-Eigenheiten bleiben bewusst erhalten

Damit sich der Umbau gegen die Baseline prüfen lässt, werden diese Eigenheiten **nachgebaut** und erst in den Folge-Changes geändert:
- Entscheidung nutzt die Geometrie der ersten und die Konfidenz der letzten Box (`multi-box-decision`)
- Aktor wird in jedem Frame beschrieben, kein Abschlusskommando, kein Reconnect (`fail-safe-shutdown`)
- Standardgerät `cpu` (`gpu-required`)
- Zufallsbilder und Detektionsbeispiele werden auch ohne `-s` geschrieben, `images/crop/` ohne Limit
- Label enthält nur die erste Box, das Detektionsbild wird ohne Boxen gespeichert
- Fehlende Ausgabeordner führen zu einer Exception
- Unbehandelte Fehler beenden das Programm mit Exit-Code 0

Ein fehlgeschlagenes `camera.read()` führt im Original über eine Exception zum Programmende. Der Kamera-Adapter wirft in diesem Fall eine Exception, das Ergebnis ist dasselbe.

### 6. Paketstruktur und Aufruf

`src/hba/` mit `capture`, `detect`, `relevance`, `decision`, `actuator`, `recorder`, `monitor`, `lifecycle`, `cli`, `app`. Aufruf über `python -m hba` mit denselben Flags und Standardwerten wie in der Baseline. `legacy/` bleibt unverändert.

### 7. Umgebung auf `hba1`

Eine virtuelle Umgebung mit `--system-site-packages` nutzt die vorhandenen torch- und ultralytics-Installationen unter `~/.local`. Das spart einen Download von mehreren GB und hält die Pins stabil. `pyproject.toml` kennt die Extras `dev` (pytest) und `gpu` (ultralytics-Pin als Dokumentation).

### 8. Transport per Git

Das Repo wird mit `git init` angelegt, ein privates GitHub-Repo dient als Gegenstelle, und `hba1` holt per `git pull` mit einem Deploy-Key. Modelle (`*.pt`), Datensätze, Logs und Umgebungen stehen in der `.gitignore`. Das Anlegen des GitHub-Repos und der Push liegen bei Jan, nicht bei Claude.

## Risks / Trade-offs

- **Der Umbau ändert unbemerkt das Verhalten** → Jedes Modul wird gegen Szenarien der Baseline-Specs geprüft. Bildaufbereitung per Golden-Test gegen die Legacy-Slicing-Zeilen, Entscheidung später zusätzlich per Replay.
- **Python 3.13 (Mac) und 3.10 (`hba1`) verhalten sich unterschiedlich** → Die Tests laufen auch auf `hba1`.
- **Die Schnittstelle des Aktors passt nicht zu `fail-safe-shutdown`** → Der Port ist so geschnitten, dass `set_status` nicht blockiert. Dieser Change liefert nur einen einfachen Legacy-Aktor, `fail-safe-shutdown` ersetzt ihn durch den Sender-Thread.
- **Mehr Abstraktion kostet Zeit pro Frame** → Bei 80 bis 120 ms pro Frame vernachlässigbar, wird im Vergleichslauf auf `hba1` gemessen.
- **Die Legacy-Mängel stehen jetzt in neuem Code** → Sie sind im Code kommentiert und verweisen auf den jeweiligen Folge-Change.

## Migration Plan

1. Paket und Tests auf dem Mac entwickeln.
2. Repo initialisieren, privates GitHub-Repo anlegen (Jan), auf `hba1` klonen und Tests dort laufen lassen.
3. Vergleichslauf auf `hba1` mit echter Kamera, GPU und Pseudo-Terminal.
4. Erst danach folgen die verhaltensändernden Changes.

Rollback: Das Legacy-Skript bleibt unverändert auf `hba1` und im Repo unter `legacy/`.

## Open Questions

- Name des GitHub-Repos (Vorschlag `JKBusse/hba-revival`). Ändert nichts an Specs oder Aufgaben.
- Sollen Typhinweise mit `mypy` geprüft werden? Kann später dazukommen.
