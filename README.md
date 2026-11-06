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

## Konfiguration

Alle Werte, die früher fest im Quelltext standen (Bildausschnitt, Aktive Fläche, Haltezeit,
Serial-Port, Stichproben, Dateilimit, Kamera, Modell), stehen in einer YAML-Datei. Eine
Beispiel-Datei mit allen Schlüsseln und den eingebauten Standardwerten liegt unter
[config/hba.example.yaml](config/hba.example.yaml). **Ohne Datei läuft das Programm mit genau diesen
Werten**, also wie bisher.

```bash
cp config/hba.example.yaml hba.yaml          # ./hba.yaml wird automatisch gelesen
python -m hba --config /pfad/zur/hba.yaml    # oder ausdrücklich angeben
```

**Vorrang:** Kommandozeilen-Flag, dann Konfigurationsdatei, dann eingebauter Standard.
Beim Start steht im Log jeder effektive Wert mit seiner Quelle (`Flag`, `Datei`, `Standard`).

**Prüfung beim Start:** Die Datei wird vor allem anderen geprüft. Unbekannte Schlüssel (zum
Beispiel ein Tippfehler `hold_secs`), falsche Typen, Werte außerhalb des Bereichs und ein
Ausschnitt, der über das Bild hinausragt, brechen den Start mit Exit-Code 2 ab. Alle Fehler
werden zusammen gemeldet:

```
Konfigurationsfehler: Unbekannter Schlüssel: decision.hold_secs
Konfigurationsfehler: image.crop_cols [400, 2000] ragt über die Bildbreite (1920) hinaus
```

Eine **Haltezeit unter 3 Sekunden** startet mit einer Warnung im Log (es gibt bewusst keine
Untergrenze). Haltezeit 0 oder negativ ist ein Fehler. Die Richtung bleibt unveränderlich:
Abblenden sofort, Aufblenden verzögert.

## Kalibrierung

Bildausschnitt und Aktive Fläche stellt man an einem Kamerabild ein. Das Werkzeug braucht weder
GPU noch Modell noch Mikrocontroller:

```bash
python -m hba.calibrate --image testbild.png --config hba.yaml
python -m hba.calibrate --camera --config hba.yaml
```

Links steht das Gesamtbild mit dem Erkennungsausschnitt (grün, verschieben und an den Ecken ziehen),
rechts der Ausschnitt als 640×640-Eingabebild des Modells mit den Grenzen der Aktiven Fläche
(gelbe Linie `min_top`, weiße Marke `max_width`), im selben Maßstab wie der Relevanzfilter.
Tasten: `s` schreibt die Werte in die Datei (nur die geänderten Schlüssel, Kommentare bleiben,
vorher läuft dieselbe Prüfung wie beim Start), `r` setzt zurück, `q` beendet ohne zu schreiben.

Auf einem Rechner ohne Display (zum Beispiel `hba1`) schreibt `--render-to ausgabe.png` nur das
Bild. Das Fenster selbst ist für den Mac gedacht; auf `hba1` reicht es, die fertige
`hba.yaml` zu kopieren. Bilder, die nicht 1920×1080 groß sind (zum Beispiel die 640×640-Bilder der
Datensätze), werden mit einem Hinweis auf die konfigurierte Auflösung skaliert.

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
