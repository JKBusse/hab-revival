# HBA Revival

Wiederbelebung des **High Beam Assist** (Fernlichtassistent): Kamera, YOLOv8-Erkennung,
Entscheidung, serielles Kommando an einen Mikrocontroller, der ein Relais schaltet
(Freigabe in Reihe mit dem Lichthebel).

- Anforderungen und Überlegungen: [REQUIREMENTS.md](REQUIREMENTS.md)
- Ist-Verhalten und geplante Änderungen: [openspec/](openspec/) (Specs unter `openspec/specs`,
  Changes unter `openspec/changes`)
- Original-Skripte von `hba1` (nur lesen): [legacy/](legacy/)

## Entwicklung auf dem Mac

Ohne GPU, Kamera und Mikrocontroller. Alles, was Hardware berührt, liegt hinter
Schnittstellen und wird in den Tests durch Fakes ersetzt.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

Python ab 3.10 (Mac: 3.13, `hba1`: 3.10). `torch` und `ultralytics` sind auf dem Mac nicht
nötig: Der Detektor importiert sie erst beim Start.

## Betrieb auf `hba1`

`hba1` (Ubuntu 22.04, Python 3.10) hat `torch` und `ultralytics` bereits unter `~/.local`.
Die virtuelle Umgebung nutzt sie mit `--system-site-packages`.

Einmalig (Deploy-Key `~/.ssh/id_ed25519_hba_deploy`, Alias `github-hba` in `~/.ssh/config`):

```bash
sudo apt-get update && sudo apt-get install -y python3.10-venv   # fehlt auf frischem Ubuntu
git clone git@github-hba:JKBusse/hab-revival.git ~/hba-revival
cd ~/hba-revival
python3 -m venv .venv --system-site-packages
.venv/bin/pip install -U pip setuptools wheel   # pip 22 kann sonst nicht editierbar installieren
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

Update: `git pull`, danach `.venv/bin/pytest`.

Das Repo ist privat. `hba1` holt es per Deploy-Key (nur lesend). Modelle (`*.pt`),
Datensätze und Logs gehören nicht ins Repo und bleiben auf `hba1`.

## Hinweise

- Vor manuellen Tests mit dem Serial-Port den Dienst anhalten (zwei Prozesse auf
  `/dev/ttyUSB0` stören sich): `sudo systemctl stop hba`.
- Das Legacy-Skript `legacy/yolov8.py` bleibt unverändert und dient als Rückfall und Referenz.
