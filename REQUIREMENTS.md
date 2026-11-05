# HBA – High Beam Assist: Anforderungen & Überlegungen

> Arbeitsdokument als Grundlage für die spätere OpenSpec-Erfassung.
> Es beschreibt den **Ist-Zustand** des bestehenden Systems (`hba1`) und die
> **Soll-Überlegungen** für das Revival. Noch kein OpenSpec-Format – hier wird
> das Rohmaterial gesammelt und in diskrete Capabilities gegliedert, damit
> daraus später `change`-Proposals / `spec`-Dateien werden können.

Stand: 2026-11-05

---

## 1. Projektüberblick

**HBA = High Beam Assist** (DIY-Fernlichtassistent). Ein selbstgebautes System,
das per Kamera und KI den Gegen-/Vorausverkehr erkennt und das **Fernlicht
automatisch ab- und wieder anschaltet** – vergleichbar mit den
Fernlichtassistenten moderner Serienfahrzeuge, aber nachrüstbar und auf Basis
von Objekterkennung (YOLOv8 / PyTorch).

**Revival-Kontext:** Das Projekt lag seit ~Mitte 2024 brach. Ziel ist es, es
wieder lauffähig zu machen, technisch zu bereinigen und für eine
spec-getriebene Weiterentwicklung (OpenSpec) aufzubereiten. Das lokale Repo
`hba-revival` ist der Neustart-Punkt; der funktionierende Alt-Stand liegt auf
dem Host `hba1`.

### Klassifikation der erkannten Objekte
- **Klasse `front` (weiße Box):** Fahrzeug von vorne (Scheinwerfer) → Gegenverkehr
- **Klasse `back` (rote Box):** Fahrzeug von hinten (Rücklichter) → Vorausfahrender
- **Ungültiges Objekt (gelbe Box):** zu hoch / zu groß / außerhalb des aktiven Bereichs

---

## 2. Funktionsprinzip (Ist-Zustand, abgeleitet aus `yolov8.py`)

Hauptschleife pro Kamerabild:

1. **Bild erfassen** von der USB-Kamera (1920×1080, MJPG), um 180° gedreht.
2. **ROI zuschneiden:**
   - `img[0:850, …]` entfernt die Spiegelung der Motorhaube.
   - `img[212:638, 400:1360]` schneidet den eigentlichen Detektionsbereich aus.
3. **Auf 640×640 skalieren** und an das YOLO-Modell geben (`best.pt`).
4. **Active-Area-Filter** (`get_active_area`): Eine Detektion gilt nur als
   „sinnvoll", wenn Boxbreite `< 500` und obere Kante `> 160` – filtert zu nahe/
   zu große oder falsch positionierte Objekte heraus.
5. **Zustandslogik (entprellt, Fail-Safe-Richtung):**
   - Bei sinnvoller Detektion wird `lastDetectTimer` aktualisiert → Fernlicht bleibt AUS.
   - Fernlicht geht **erst wieder AN (`hbaStatus = 1`), wenn die letzte Detektion
     ≥ 3 s zurückliegt** – also nur nach durchgehend freier Sicht.
   - Solange innerhalb der letzten 3 s detektiert wurde → `hbaStatus = 0` (AUS / abblenden).
   - **Rationale:** Die Haltezeit entprellt gegen **False Negatives**. Ein
     einzelner verpasster Frame (Auto kurzzeitig nicht erkannt) darf das
     Fernlicht **nicht** sofort anschalten und Gegenverkehr blenden. Erst wenn
     über mehrere Sekunden *kein* Fahrzeug erkannt wird, wird aufgeblendet.
     Das Abblenden (AUS) erfolgt dagegen sofort bei der ersten Detektion.
6. **Ausgabe über Serial** (`/dev/ttyUSB0`, 9600 Baud, CH341 USB-UART):
   schreibt `"1\n"` bzw. `"0\n"` an einen Mikrocontroller, der das
   Fernlicht-Relais schaltet.
7. **Datensammlung** (optional, `--save`): speichert Crops, Zufalls-Frames und
   Detektions-Bilder inkl. automatisch generierter YOLO-Labels; Rotation per
   `maxFiles` (max. 1000 Dateien je Ordner).
8. **Visualisierung** (optional): Live-Fenster (`--video`) oder MJPEG-Stream
   via Flask (`stream.py`, Port 5000) für Remote-Monitoring.
9. **Logging** in Dateien (`--path/log/<timestamp>.log`).

---

## 3. Hardware (Ist)

| Komponente | Details |
|---|---|
| Rechner | Mini-PC, Intel i3-5010U (4 Threads @ 2,0 GHz), 3,7 GB RAM |
| GPU | NVIDIA P106-100 (Mining-Variante der GTX 1060, kein Videoausgang) |
| Kamera | USB-Kamera, v4l2-gesteuert (manuelle Belichtung, 50 Hz Powerline) |
| Aktorik | Mikrocontroller via CH341 USB-UART → Relais → Fernlicht |
| Sensorik | CPU-Temperatur (`psutil`, `sensors1.py`); ggf. weitere geplant |
| Storage | System-SSD + USB-Stick (`/mnt/hba-stick`, „WIS") für Bilder/Logs |
| OS | Ubuntu 22.04.4 LTS, Kernel 6.8 |

---

## 4. Software-Stack (Ist)

- **Python 3** mit `ultralytics` (YOLOv8), `opencv-python`, `pyserial`,
  `numpy`, `psutil`, `flask`.
- CUDA/NVIDIA-Treiber für GPU-Inferenz (optional TensorRT `.engine`).
- `v4l2-ctl` für Kamerasteuerung.
- Kommandozeilen-Flags: `-v` Video, `-S` Stream, `-s` Save, `-c` Confidence
  (Default 0.4), `-d` Device (cpu/cuda), `-m` Modellpfad, `-e/-t/-b` Belichtung,
  `-p` Speicherpfad.

---

## 5. Daten & Modell

### Datasets (Roboflow-Exporte, YOLOv8-Format, 2 Klassen)
| Dataset | Roboflow | Version | train/valid/test | Klassen |
|---|---|---|---|---|
| `HBA1-Datasets/V1/HBA2` | `jkb/hba2` | v5 | 205 / 59 / 29 | `Back`, `Front` |
| `HBA4v2Dataset` | `jkb-rzgt3/hba4` | v11 | 3309 / 353 / 182 | `back`, `front` |

**Bekannte Daten-Auffälligkeiten (`HBA4v2Dataset/train`, analysiert 2026-11-05):**
Der train-Split besteht aus zwei getrennten Populationen:
- **A – Roboflow-verarbeitet** (`*.rf.<hash>`, .jpg, 1294 Bilder): 800 mit
  Boxen, **495 leere Label-Dateien** (davon 487 Präfix `OFF…`). Die leeren
  Labels sind **gewollte Negativbilder** (reduzieren False Positives) → behalten.
- **B – Roh-Captures** (reiner Zeitstempel-Name, .png, 2015 Bilder): 1559
  gelabelt, **456 ganz ohne Label-Datei**. Das sind **unannotierte Reste** aus
  dem Live-System (`yolov8.py` speichert Frames als `<timestamp>.png`), **keine**
  bewussten Negative.
- ⚠️ **Risiko:** YOLO wertet Bilder ohne Label-Datei als Hintergrund. Enthalten
  die 456 Roh-Frames Fahrzeuge (wahrscheinlich), trainiert man dem Modell
  False Negatives an → gefährlich (vgl. §8). **Vor Re-Training nachlabeln oder
  entfernen**, nicht als implizite Negative belassen.
- 4 verwaiste Label-Dateien ohne zugehöriges Bild (harmloser Aufräumpunkt).
- Uneinheitliche Klassenschreibweise zwischen Versionen (`Back/Front` vs.
  `back/front`) – Vorsicht beim Mischen alter/neuer Daten & Modelle.
- Aktives Lernen: Das Live-System speichert automatisch gelabelte Detektionen
  zur Dataset-Erweiterung.

### Modell
- Aktuell referenziert: `HBA4v2Dataset/HBAv5/medium6/weights/best.pt`
  (YOLOv8-medium). TensorRT-`.engine` als schnellere Alternative erwähnt.

---

## 6. Funktionale Anforderungen (Capabilities)

Gegliedert als eigenständige Capabilities – bewusst so geschnitten, dass daraus
je eine OpenSpec-Spec werden kann.

### FR-1 Bilderfassung
- Kamera initialisieren, Auflösung/Format/Belichtung deterministisch setzen.
- Belichtung manuell fixierbar (Nachtfahrt, keine Auto-Belichtung).
- Bildorientierung und ROI/Crop konfigurierbar (nicht hartkodiert).

### FR-2 Objekterkennung
- YOLOv8-Inferenz auf dem zugeschnittenen Bild.
- Unterscheidung `front` (Gegenverkehr) / `back` (Vorausfahrender).
- Konfigurierbare Confidence-Schwelle.
- Lauffähig auf GPU (Primärziel) mit CPU-Fallback.

### FR-3 Relevanzfilter („Active Area")
- Detektionen nach Position/Größe filtern (relevante Fahrzeuge vs. Störobjekte).
- Schwellen konfigurierbar statt hartkodiert (aktuell: Breite < 500, obere Kante > 160).

### FR-4 Fernlicht-Entscheidungslogik
- Zustand AN/AUS aus den gefilterten Detektionen ableiten.
- **Asymmetrische Entprellung (sicherheitskritisch, bestätigt):**
  - **Abblenden (AUS) sofort** bei der ersten sinnvollen Detektion.
  - **Aufblenden (AN) nur verzögert** nach ≥ 3 s durchgehend ohne Detektion.
  - Zweck: einzelne/mehrere **False Negatives** dürfen nicht zum Blenden führen.
- Haltezeit konfigurierbar (aktuell 3 s), aber Richtung (AUS schnell, AN langsam)
  muss erhalten bleiben.
- Klar definiertes, sicheres Standardverhalten bei Unsicherheit (AUS).

### FR-5 Aktor-Ansteuerung
- Zustand an Mikrocontroller über Serial senden.
- Robust gegen Verbindungsverlust (Reconnect / sicherer Fallback).
- Definiertes Protokoll zwischen PC und Mikrocontroller.

### FR-6 Datensammlung & aktives Lernen
- Optionales Speichern von Roh-/Crop-/Detektionsbildern + Auto-Labels.
- Speicherplatz-Begrenzung (Datei-Rotation).
- Export-/Übergabeweg zu Roboflow/Trainingspipeline.

### FR-7 Monitoring & Visualisierung
- Lokales Video-Fenster und/oder Remote-MJPEG-Stream.
- Logging von Ereignissen, Timings (FPS) und Zuständen.
- System-Telemetrie (CPU-/GPU-Temperatur) überwachen.

### FR-8 Konfiguration & Betrieb
- Parameter per CLI/Config statt hartkodierter Pfade (`/home/jkb/...`).
- Autostart im Fahrzeug (Service), sauberes Start/Stop-Verhalten.
- Nachvollziehbares Verhalten bei Kamera-/Modell-/Serial-Fehlern.

---

## 7. Nicht-funktionale Anforderungen

- **Echtzeit:** ausreichende Framerate für Fahrgeschwindigkeit; Latenz Kamera→
  Fernlicht gering und begründet (aktuell `DIFF`-Logging pro Frame).
- **Zuverlässigkeit:** Dauerbetrieb ohne Absturz; Auto-Recovery nach Fehlern.
- **Robustheit:** definiertes Verhalten bei Teil-Ausfällen (Kamera/GPU/Serial).
- **Ressourcen:** lauffähig innerhalb 3,7 GB RAM und der P106-100-GPU.
- **Wartbarkeit:** konfigurierbar, testbar, keine Magic Numbers / Fixpfade.
- **Portabilität:** Treiber-/Umgebungsabhängigkeiten reproduzierbar (siehe §9).

---

## 8. Sicherheits- & Rechtsüberlegungen (wichtig)

> Kritisch, weil das System aktiv in die Fahrzeugbeleuchtung eingreift.

- **Fail-Safe:** Im Zweifel / bei jedem Fehler muss **abgeblendet** werden
  (Fernlicht AUS ist der sichere Zustand), nicht umgekehrt.
- **Gegenverkehr darf nie geblendet werden** → false-negative (Fahrzeug nicht
  erkannt) ist der gefährliche Fehlerfall; Erkennungsrate hier priorisieren.
  Deshalb die asymmetrische Entprellung (FR-4): sofort abblenden, nur nach
  längerer freier Sicht aufblenden.
- **Manueller Override / Not-Aus:** per **Hardware gelöst** (Stand 2026-11-06). Das
  Relais ist als *Freigabe in Reihe* mit dem Lichthebel verbaut. Der Assistent kann
  Fernlicht nur erlauben oder sperren, nie erzwingen. Fällt er aus, fährt der
  Fahrer mit Abblendlicht. Keine Software-Anforderung, aber Randbedingung für alle
  Changes (siehe `openspec/changes/`). Der Firmware-Timeout (1 bis 3 s ohne Kommando
  blendet der Mikrocontroller selbst ab) ist die zweite Absicherung.
- **Latenz-Budget:** Reaktionszeit muss kurz genug sein, dass Gegenverkehr
  rechtzeitig abgeblendet wird.
- **Zulassung/StVZO:** Eingriff in die Beleuchtungsanlage ist rechtlich heikel;
  Status als Experimental-/Erprobungssystem klar dokumentieren.
- **Robustheit gegen Bedingungen:** Regen, Nebel, verschmutzte Linse,
  Reflexionen, Schilder/Reflektoren (Fehlauslöser).

---

## 9. Bekannter Ist-Zustand / technische Schulden

- ⚠️ **GPU wird beim Boot nicht enumeriert** (diagnostiziert & gelöst
  2026-11-05): Treiber 535.183.01 + DKMS für Kernel 6.8 sind korrekt. Die
  P106-100 (an Root-Port `00:1c.3`, Link nur x1 @ 2,5 GT/s – langsamer
  Mining-Riser) erscheint **nach einem Boot nicht automatisch** auf dem Bus,
  daher scheitert `nvidia-smi`. **Workaround (funktioniert):**
  `echo 1 | sudo tee /sys/bus/pci/rescan` + `sudo modprobe nvidia nvidia_uvm
  nvidia_modeset` → Karte erscheint als `03:00.0`, `nvidia-smi` läuft, PyTorch
  2.0.1+cu117 meldet `cuda=True`, ultralytics 8.0.180 vorhanden.
  **Offen:** Rescan+modprobe überlebt keinen Reboot → sollte als Boot-Service
  (systemd oneshot) automatisiert werden; Ursache (Link trainiert zu spät für
  BIOS-POST) ggf. zusätzlich im BIOS/per Kernel-Param adressieren.
- ⛔ **GPU bricht unter Last ab – Hardware-/Stromfehler (bestätigt 2026-11-05):**
  Stresstest (PyTorch-matmul) zeigt: die Karte **fällt vom PCI-Bus, sobald sie
  den Takt hochfährt** (139→1506 MHz) – bei nur **~27 W**, weit unter dem
  gesetzten 90-W-Limit. Danach `CUDA error: invalid device ordinal` /
  `Unable to determine the device handle`, teils Komplett-Reboot der Maschine.
  Also **kein Volllast-Brownout**, sondern Abriss am Clock-Boost-Transienten →
  deutet auf **lockere/marginale Stromverbindung (PCIe-Power-Stecker),
  schlechten Riser oder schwaches/gealtertes Netzteil** hin. **Softwareseitig
  nicht lösbar.** Zu prüfen (physisch): PCIe-Stromstecker + Kabel der GPU
  reseaten, Riser-Stromversorgung + Riser/USB-Kabel prüfen/tauschen, anderes/
  stärkeres Netzteil testen. **Blockiert GPU-Training/-Inferenz komplett, bis
  behoben.** Interims-Workaround-Idee (ungetestet): GPU-Takt per
  `nvidia-smi -lgc` niedrig locken, damit der tripauslösende Boost-Transient
  ausbleibt.
  **Update nach neuer Stromversorgung (2026-11-05, abends):** Boot-Enumeration
  klappte diesmal von selbst. Boost-Transient wird jetzt überstanden. Test 1
  (90-W-Limit, n=2048, 15 s): stabil, ~88 W, 42 °C. Test 2 (120-W-Limit,
  n=4096): stabil bis ~60 s bei ~115–118 W, 1822 MHz, 60 °C, Lüfter 59 %, dann
  `Xid 79: GPU has fallen off the bus` (ohne vorherige AER-Fehler; OS blieb
  oben, GPU danach `rev ff` und nur per Reboot zurückholbar). Abriss also erst
  bei längerer Dauerlast nahe Limit → verbleibende Kandidaten: PCIe-Stromstecker/
  Kabel der GPU, Riser/x1-Link, 12-V-Rail unter Dauerlast. Thermisch (60 °C)
  unwahrscheinlich. Nächster Schritt: stabile Betriebsgrenze ermitteln
  (z. B. Dauertest bei 90 W / niedrigerem Takt) und Riser/Stecker prüfen.
- Hartkodierte Pfade (`/home/jkb/...`, `/mnt/hba-stick/...`).
- Magic Numbers für Crop/Active-Area ohne Kalibrierungs-/Begründungsmechanismus.
- `yolov8.py` als ein monolithisches Skript (Erfassung, Inferenz, Logik,
  Ausgabe, Daten, UI vermischt) → für Specs/Tests schwer zu schneiden.
- Breites `except:` ohne spezifische Fehlerbehandlung.
- Kein Autostart-/Service-Setup dokumentiert.
- Mikrocontroller-Firmware (Empfänger der `0/1`-Befehle) nicht im Repo.

---

## 10. Offene Fragen / zu klärende Entscheidungen

1. ~~Sind die 452 unlabeled Bilder in HBA4v2 gewollte Negativbilder?~~
   **Geklärt (2026-11-05):** Nein. Gewollte Negative sind die 495 leeren
   `OFF…`-Labels; die 456 Bilder ohne Label sind unannotierte Roh-Captures →
   vor Re-Training nachlabeln oder entfernen (siehe §5).
2. Zielplattform des Revivals: weiter `hba1` (P106-100) oder neue HW (z. B.
   Jetson / aktuellere GPU)?
3. Soll das Serial-Protokoll um Rückkanal/Statusabfrage erweitert werden?
4. Wie wird kalibriert (Kameraposition/ROI) bei Einbau in ein anderes Fahrzeug?
5. Welche Zielmetriken (mAP, Reaktionszeit, FPS) definieren „gut genug"?
6. Datenschutz/Aufbewahrung der gespeicherten Fahrtbilder?
7. Mikrocontroller-Firmware ins Repo aufnehmen / spezifizieren?

---

## 11. Revival-Ziele (Vorschlag, zu priorisieren)

1. **Lauffähigkeit wiederherstellen** (NVIDIA-Treiber/CUDA auf `hba1`).
2. **Code modularisieren** entlang der Capabilities aus §6 (Erfassung /
   Inferenz / Logik / Aktor / Daten / Monitoring getrennt).
3. **Konfiguration externalisieren** (Config-Datei statt Fixpfade/Magic Numbers).
4. **Dataset konsolidieren** (Label-Lücke klären, Klassen vereinheitlichen,
   neu trainieren/evaluieren).
5. **Fail-Safe-Verhalten** explizit spezifizieren und testen (Override ist per
   Hardware gelöst, siehe §8).
6. Darauf aufbauend **OpenSpec-Specs** je Capability schreiben.

---

*Quellen: `~/FLA1`, `~/yolov8.py`, `~/stream.py`, `~/sensors1.py` auf `hba1`
(192.168.2.37) sowie die lokalen Datasets `HBA1-Datasets` und `HBA4v2Dataset`.*
